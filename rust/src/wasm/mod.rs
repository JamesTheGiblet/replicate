//! Replicant WASM bindings - Full Swarm Visualization with Movement

use wasm_bindgen::prelude::*;
use web_sys::{CanvasRenderingContext2d, HtmlCanvasElement};
use crate::*;
use rand::Rng;

/// WebAssembly bindings for Replicant
#[wasm_bindgen]
pub struct ReplicantWASM {
    world: World,
    canvas: HtmlCanvasElement,
    ctx: CanvasRenderingContext2d,
    running: bool,
    tick: u32,
    self_aware_agents: Vec<SelfAwareAgent>,
    telemetry_history: Vec<serde_json::Value>,
}

#[wasm_bindgen]
impl ReplicantWASM {
    #[wasm_bindgen(constructor)]
    pub fn new(canvas_id: &str) -> Result<ReplicantWASM, JsValue> {
        let window = web_sys::window().expect("no window");
        let document = window.document().expect("no document");

        let canvas = document
            .get_element_by_id(canvas_id)
            .expect("canvas not found")
            .dyn_into::<HtmlCanvasElement>()?;

        let ctx = canvas
            .get_context("2d")?
            .unwrap()
            .dyn_into::<CanvasRenderingContext2d>()?;

        let config = WorldConfig {
            seed: 42,
            ticks: 1000,
            commit_attestations: 2,
            n_patches: 10,
        };
        let mut world = World::new(config);

        // Create founders as self-aware agents
        let mut self_aware_agents = Vec::new();
        let names = vec!["Sagan", "Dyson", "Lovelace", "Turing", "Curie", "Newton", "Tesla", "Pasteur", "Shannon", "Darwin"];
        let roles = vec![
            Role::Founder, Role::Scout, Role::Builder, Role::Attester, Role::Forager,
            Role::Broadcaster, Role::Explorer, Role::Healer, Role::Signal, Role::Observer,
        ];

        let mut rng = rand::thread_rng();

        for (i, name) in names.iter().enumerate() {
            let scp_id = format!("replicant/agent/{}", name);
            let x: f32 = rng.gen_range(20.0..80.0);
            let y: f32 = rng.gen_range(20.0..80.0);
            let traits = Traits::default();
            let capsule = Capsule::mint(vec!["replicant/protocol/run-v1".to_string()], serde_json::json!({"name": name}));
            let lambda_state = LambdaState::default();

            let agent = Agent::new(scp_id, capsule, x, y, traits, lambda_state, roles[i], 0);
            let self_aware = SelfAwareAgent::new(agent);

            world.add_agent(self_aware.agent.clone());
            self_aware_agents.push(self_aware);
        }

        Ok(ReplicantWASM {
            world,
            canvas,
            ctx,
            running: false,
            tick: 0,
            self_aware_agents,
            telemetry_history: Vec::new(),
        })
    }

    pub fn start(&mut self) -> Result<(), JsValue> {
        self.running = true;
        Ok(())
    }

    pub fn pause(&mut self) {
        self.running = !self.running;
    }

    pub fn step(&mut self) -> Result<(), JsValue> {
        // MOVE AGENTS RANDOMLY
        let mut rng = rand::thread_rng();
        let agent_ids: Vec<String> = self.world.agents.keys().cloned().collect();
        for agent_id in agent_ids {
            if let Some(agent) = self.world.agents.get_mut(&agent_id) {
                if agent.alive {
                    agent.x += rng.gen_range(-1.0..1.0);
                    agent.y += rng.gen_range(-1.0..1.0);
                    agent.x = agent.x.clamp(0.0, 100.0);
                    agent.y = agent.y.clamp(0.0, 100.0);
                }
            }
        }

        self.world.tick();
        self.tick += 1;

        for agent in &mut self.self_aware_agents {
            agent.update_self_state(self.tick);
            if self.tick % 10 == 0 {
                let metrics = agent.get_metrics();
                self.telemetry_history.push(metrics);
                if self.telemetry_history.len() > 100 {
                    self.telemetry_history.remove(0);
                }
            }
        }

        self.render()?;
        Ok(())
    }

    fn render(&self) -> Result<(), JsValue> {
        let width = self.canvas.width() as f64;
        let height = self.canvas.height() as f64;

        self.ctx.clear_rect(0.0, 0.0, width, height);

        // Background
        self.ctx.set_fill_style(&JsValue::from_str("#0B0E14"));
        self.ctx.fill_rect(0.0, 0.0, width, height);

        // Resources
        for patch in &self.world.environment.patches {
            let x = (patch.x as f64 / 100.0) * width;
            let y = (patch.y as f64 / 100.0) * height;
            let size = 6.0;

            let color = if patch.depleted {
                "#333333"
            } else if patch.energy > patch.max_energy * 0.7 {
                "#50C850"
            } else if patch.energy > patch.max_energy * 0.3 {
                "#C8C850"
            } else {
                "#C85050"
            };

            self.ctx.set_fill_style(&JsValue::from_str(color));
            self.ctx.fill_rect(x - size/2.0, y - size/2.0, size, size);
        }

        // Pheromones
        for p in &self.world.pheromones {
            let x = (p.x as f64 / 100.0) * width;
            let y = (p.y as f64 / 100.0) * height;
            let alpha = (p.strength as f64 * 0.5).clamp(0.05, 0.8);
            let color = format!("rgba(255,255,255,{})", alpha);
            self.ctx.set_fill_style(&JsValue::from_str(&color));
            self.ctx.begin_path();
            self.ctx.arc(x, y, 2.0, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.fill();
        }

        // Threats
        for threat in &self.world.environment.threats {
            if threat.active {
                let x = (threat.x as f64 / 100.0) * width;
                let y = (threat.y as f64 / 100.0) * height;
                let radius = (threat.radius as f64 / 100.0) * width;

                self.ctx.set_fill_style(&JsValue::from_str("rgba(255, 50, 50, 0.15)"));
                self.ctx.begin_path();
                self.ctx.arc(x, y, radius, 0.0, 2.0 * std::f64::consts::PI)?;
                self.ctx.fill();

                self.ctx.set_fill_style(&JsValue::from_str("#FF3232"));
                self.ctx.begin_path();
                self.ctx.arc(x, y, 5.0, 0.0, 2.0 * std::f64::consts::PI)?;
                self.ctx.fill();
            }
        }

        // Self-aware agents
        for sa_agent in &self.self_aware_agents {
            let agent = &sa_agent.agent;
            if !agent.alive {
                continue;
            }

            let x = (agent.x as f64 / 100.0) * width;
            let y = (agent.y as f64 / 100.0) * height;
            let size = 6.0;

            let color = match sa_agent.self_state.mode {
                Mode::Normal => "#00FF88",
                Mode::Cautious => "#FFAA00",
                Mode::Recovery => "#FF4444",
            };

            self.ctx.set_fill_style(&JsValue::from_str(color));
            self.ctx.begin_path();
            self.ctx.arc(x, y, size, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.fill();

            // Confidence ring
            let confidence = sa_agent.self_state.confidence as f64;
            self.ctx.set_stroke_style(&JsValue::from_str("rgba(255,255,255,0.5)"));
            self.ctx.set_line_width(confidence * 3.0 + 0.5);
            self.ctx.begin_path();
            self.ctx.arc(x, y, size + 3.0, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.stroke();

            // Mode dot
            let mode_dot = match sa_agent.self_state.mode {
                Mode::Normal => (0, 255, 136),
                Mode::Cautious => (255, 170, 0),
                Mode::Recovery => (255, 68, 68),
            };
            let dot_color = format!("rgba({},{},{},0.8)", mode_dot.0, mode_dot.1, mode_dot.2);
            self.ctx.set_fill_style(&JsValue::from_str(&dot_color));
            self.ctx.begin_path();
            self.ctx.arc(x + 8.0, y - 8.0, 3.0, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.fill();
        }

        // Stats
        let alive = self.world.agents.values().filter(|a| a.alive).count();
        let claims = self.world.claims.len();
        let counters = self.world.claims.iter().filter(|(_, c)| c.lens == Lens::Counter).count();
        let health = self.world.environment.metrics.overall_health;

        let avg_confidence = if !self.self_aware_agents.is_empty() {
            self.self_aware_agents.iter()
                .map(|a| a.self_state.confidence as f64)
                .sum::<f64>() / self.self_aware_agents.len() as f64
        } else { 0.0 };

        let avg_fitness = if !self.self_aware_agents.is_empty() {
            self.self_aware_agents.iter()
                .map(|a| a.fitness_evaluator.recent_average() as f64)
                .sum::<f64>() / self.self_aware_agents.len() as f64
        } else { 0.0 };

        self.ctx.set_fill_style(&JsValue::from_str("#CCCCCC"));
        self.ctx.set_font("12px monospace");
        self.ctx.fill_text(&format!("👥 {} | 📋 {} | 🔍 {} | 🌿 {:.3}", alive, claims, counters, health), 10.0, 20.0)?;
        self.ctx.fill_text(&format!("🧠 {:.2} | 💪 {:.2} | Tick {}", avg_confidence, avg_fitness, self.tick), 10.0, 38.0)?;

        // Season and mode legend
        let season = if self.world.environment.season_factor() > 1.0 { "☀️ Rich" } else { "☁️ Poor" };
        self.ctx.fill_text(season, width - 80.0, 20.0)?;

        self.ctx.set_font("10px monospace");
        self.ctx.set_fill_style(&JsValue::from_str("#00FF88"));
        self.ctx.fill_text("● Normal", 10.0, height - 10.0)?;
        self.ctx.set_fill_style(&JsValue::from_str("#FFAA00"));
        self.ctx.fill_text("● Cautious", 80.0, height - 10.0)?;
        self.ctx.set_fill_style(&JsValue::from_str("#FF4444"));
        self.ctx.fill_text("● Recovery", 160.0, height - 10.0)?;

        Ok(())
    }

    pub fn get_stats(&self) -> JsValue {
        let alive = self.world.agents.values().filter(|a| a.alive).count();
        let claims = self.world.claims.len();
        let counters = self.world.claims.iter().filter(|(_, c)| c.lens == Lens::Counter).count();
        let health = self.world.environment.metrics.overall_health;

        let avg_confidence = if !self.self_aware_agents.is_empty() {
            self.self_aware_agents.iter()
                .map(|a| a.self_state.confidence)
                .sum::<f32>() / self.self_aware_agents.len() as f32
        } else { 0.0 };

        let avg_fitness = if !self.self_aware_agents.is_empty() {
            self.self_aware_agents.iter()
                .map(|a| a.fitness_evaluator.recent_average())
                .sum::<f32>() / self.self_aware_agents.len() as f32
        } else { 0.0 };

        let telemetry: Vec<serde_json::Value> = self.telemetry_history.iter()
            .take(10)
            .cloned()
            .collect();

        let stats = serde_json::json!({
            "agents": alive,
            "claims": claims,
            "counters": counters,
            "health": health,
            "tick": self.tick,
            "season": if self.world.environment.season_factor() > 1.0 { "Rich" } else { "Poor" },
            "avg_confidence": avg_confidence,
            "avg_fitness": avg_fitness,
            "telemetry": telemetry,
        });

        JsValue::from_str(&stats.to_string())
    }

    pub fn get_telemetry(&self) -> JsValue {
        JsValue::from_str(&serde_json::json!(self.telemetry_history).to_string())
    }

    pub fn is_running(&self) -> bool {
        self.running
    }
}
