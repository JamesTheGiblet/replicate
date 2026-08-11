//! Replicant - Hybrid bio-inspired swarm framework
//!
//! Born pregnant. Born ready. Born signed.
//! The swarm learns. The liar pays.

pub mod core;
pub mod agent;
pub mod world;
pub mod environment;
pub mod adversary;
pub mod viz;

// Re-exports
pub use core::*;
pub use agent::*;
pub use world::*;
pub use environment::*;
pub use adversary::*;
pub use viz::*;
