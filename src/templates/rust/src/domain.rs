//! Domain layer - бизнес-сущности и логика предметной области

use std::fmt::Debug;
use time::OffsetDateTime;

/// Базовая сущность с идентичностью
pub trait Entity: Debug + Send + Sync {
    fn id(&self) -> &str;
    fn created_at(&self) -> OffsetDateTime;
    fn updated_at(&self) -> Option<OffsetDateTime>;
}

/// Value Object - неизменяемый объект без идентичности
pub trait ValueObject: Clone + Debug + PartialEq + Send + Sync {}

/// Базовая реализация для сущностей
#[derive(Debug, Clone)]
pub struct BaseEntity {
    pub id: String,
    pub created_at: OffsetDateTime,
    pub updated_at: Option<OffsetDateTime>,
}

impl BaseEntity {
    pub fn new(id: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            created_at: OffsetDateTime::now_utc(),
            updated_at: None,
        }
    }

    pub fn update_timestamp(&mut self) {
        self.updated_at = Some(OffsetDateTime::now_utc());
    }
}

impl Entity for BaseEntity {
    fn id(&self) -> &str {
        &self.id
    }

    fn created_at(&self) -> OffsetDateTime {
        self.created_at
    }

    fn updated_at(&self) -> Option<OffsetDateTime> {
        self.updated_at
    }
}

/// Агрегат - кластер объектов как единое целое
pub trait AggregateRoot: Entity {
    type Event: Debug + Send + Sync;
    
    fn domain_events(&self) -> &[Self::Event];
    fn clear_events(&mut self);
}
