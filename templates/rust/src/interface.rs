//! Interface layer - Controllers и DTOs

use crate::application::{DTO, UseCase};
use std::fmt::Debug;

/// Response DTO
#[derive(Debug, Clone)]
pub struct ResponseDTO<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl<T> ResponseDTO<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    pub fn error(message: impl Into<String>) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message.into()),
        }
    }
}

/// Request DTO трейт
pub trait RequestDTO: Clone + Debug + Send + Sync {
    fn validate(&self) -> Result<(), String>;
}

/// Base Controller
pub struct Controller;

impl Controller {
    pub async fn handle_request<U, TReq, TRes>(
        &self,
        request: TReq,
        use_case: &U,
    ) -> ResponseDTO<TRes>
    where
        U: UseCase<Request = TReq, Response = TRes>,
        TReq: Send + Sync,
        TRes: Send + Sync,
        <U as UseCase>::Error: Debug,
    {
        match use_case.execute(request).await {
            Ok(result) => ResponseDTO::success(result),
            Err(e) => ResponseDTO::error(format!("{:?}", e)),
        }
    }
}
