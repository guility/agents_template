//! Infrastructure layer - реализация портов

use crate::application::Repository;
use crate::domain::Entity;
use async_trait::async_trait;
use std::collections::HashMap;
use std::fmt::Debug;
use tokio::sync::RwLock;

/// In-Memory Repository для тестирования
pub struct InMemoryRepository<T>
where
    T: Entity + Debug + Clone,
{
    storage: RwLock<HashMap<String, T>>,
}

impl<T> InMemoryRepository<T>
where
    T: Entity + Debug + Clone,
{
    pub fn new() -> Self {
        Self {
            storage: RwLock::new(HashMap::new()),
        }
    }
}

impl<T> Default for InMemoryRepository<T>
where
    T: Entity + Debug + Clone,
{
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl<T> Repository<T> for InMemoryRepository<T>
where
    T: Entity + Debug + Clone + Send + Sync,
{
    type Error = RepositoryError;

    async fn find_by_id(&self, id: &str) -> Result<Option<T>, Self::Error> {
        let storage = self.storage.read().await;
        Ok(storage.get(id).cloned())
    }

    async fn find_all(&self) -> Result<Vec<T>, Self::Error> {
        let storage = self.storage.read().await;
        Ok(storage.values().cloned().collect())
    }

    async fn save(&self, entity: T) -> Result<(), Self::Error> {
        let mut storage = self.storage.write().await;
        storage.insert(entity.id().to_string(), entity);
        Ok(())
    }

    async fn delete(&self, id: &str) -> Result<(), Self::Error> {
        let mut storage = self.storage.write().await;
        storage.remove(id);
        Ok(())
    }
}

/// Ошибка репозитория
#[derive(Debug, Clone)]
pub enum RepositoryError {
    NotFound(String),
    Conflict(String),
    Internal(String),
}

impl std::fmt::Display for RepositoryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RepositoryError::NotFound(msg) => write!(f, "Not found: {}", msg),
            RepositoryError::Conflict(msg) => write!(f, "Conflict: {}", msg),
            RepositoryError::Internal(msg) => write!(f, "Internal error: {}", msg),
        }
    }
}

impl std::error::Error for RepositoryError {}
