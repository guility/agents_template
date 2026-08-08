//! Application layer - Use Cases и Ports (интерфейсы)

use crate::domain::Entity;
use async_trait::async_trait;
use std::fmt::Debug;

/// Repository Port - интерфейс для репозиториев
#[async_trait]
pub trait Repository<T>: Send + Sync
where
    T: Entity + Debug,
{
    type Error: Debug;

    async fn find_by_id(&self, id: &str) -> Result<Option<T>, Self::Error>;
    async fn find_all(&self) -> Result<Vec<T>, Self::Error>;
    async fn save(&self, entity: T) -> Result<(), Self::Error>;
    async fn delete(&self, id: &str) -> Result<(), Self::Error>;
}

/// Use Case интерфейс
#[async_trait]
pub trait UseCase {
    type Request: Send + Sync;
    type Response: Send + Sync;
    type Error: Debug;

    async fn execute(&self, request: Self::Request) -> Result<Self::Response, Self::Error>;
}

/// DTO базовый трейт
pub trait DTO: Clone + Debug + Send + Sync {}
