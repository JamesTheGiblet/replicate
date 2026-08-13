//! Replicant Benchmark Binary

use replicant::*;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut agents = 10;
    let mut ticks = 200;
    let mut seed = 42;
    
    for i in 0..args.len() {
        if args[i] == "--agents" && i + 1 < args.len() {
            agents = args[i + 1].parse().unwrap_or(10);
        }
        if args[i] == "--ticks" && i + 1 < args.len() {
            ticks = args[i + 1].parse().unwrap_or(200);
        }
        if args[i] == "--seed" && i + 1 < args.len() {
            seed = args[i + 1].parse().unwrap_or(42);
        }
    }
    
    let config = WorldConfig {
        seed,
        ticks: ticks as u32,
        commit_attestations: 2,
        n_patches: 10,
    };
    
    let mut world = World::new(config);
    
    // Create agents directly with full constructor
    for i in 0..agents {
        let scp_id = format!("agent_{}", i);
        let x = (i as f32 * 5.0) % 90.0 + 5.0;
        let y = (i as f32 * 3.0) % 90.0 + 5.0;
        let traits = Traits::default();
        let role = if i == 0 { Role::Founder } else { Role::Forager };
        let capsule = Capsule::mint(vec!["replicant/protocol/run-v1".to_string()], serde_json::json!({}));
        let lambda_state = LambdaState::default();
        let agent = Agent::new(scp_id, capsule, x, y, traits, lambda_state, role, 0);
        world.add_agent(agent);
    }
    
    // Run the simulation
    let start = std::time::Instant::now();
    for _ in 0..ticks {
        world.tick();
    }
    let duration = start.elapsed();
    
    // Collect stats
    let alive = world.agents.values().filter(|a| a.alive).count();
    let claims = world.claims.len();
    let counters = world.claims.iter().filter(|(_, c)| c.lens == Lens::Counter).count();
    let health = world.environment.metrics.overall_health;
    
    let stats = serde_json::json!({
        "alive": alive,
        "claims": claims,
        "counters": counters,
        "health": health,
    });
    
    let result = serde_json::json!({
        "time_sec": duration.as_secs_f64(),
        "stats": stats,
    });
    
    println!("{}", serde_json::to_string(&result).unwrap());
}
