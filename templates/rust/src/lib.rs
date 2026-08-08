//! DDD Rust Template
//! 
//! Domain-Driven Design с чистой архитектурой

pub mod domain;
pub mod application;
pub mod infrastructure;
pub mod interface;

// Re-exports
pub use domain::*;
pub use application::*;
pub use infrastructure::*;
pub use interface::*;
