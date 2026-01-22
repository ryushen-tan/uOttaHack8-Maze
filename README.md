# Snowy Day ❄️ 🚛

> **Maps + AI + Real-time visuals = Satisfying snow-clearing chaos.**

**Snowy Day** is a reinforcement learning experiment designed to tackle the chaos of winter snow clearing. It simulates autonomous snowplows acting as intelligent agents, optimizing routes in real-time to clear city streets with minimal overlap and maximum efficiency.

[![Live Demo](https://img.shields.io/badge/demo-live-green.svg)](https://snowyday.tech)
[![GitHub](https://img.shields.io/badge/github-repo-blue.svg)](https://github.com/your-username/snowy-day)

## 📖 Inspiration

It snowed. A lot. Our streets turned into chaos, traffic slowed to a crawl, and snowplows somehow still missed half the roads. We started wondering: **why are snowplow routes still basically guesswork?**

That curiosity turned into **Snowy Day**—a fun experiment to see how much better snowplowing could be with a little AI help.

## 🕹️ What It Does

Snowy Day lets you pick a city and watch snowplows clean it up the smart way.

* **Intelligent Agents:** Each snowplow acts like its own independent "brain," figuring out where to go next.
* **Optimization:** The AI ensures every road gets cleared with as little overlap and wasted time as possible.
* **Real-Time Simulation:** Watch the plows move live as they tackle streets, highways, and intersections collaboratively.

## 🛠️ How We Built It

We built Snowy Day as a full-stack web application, combining map data with a custom reinforcement learning model.

### Tech Stack
* **Frontend:** [React.js](https://reactjs.org/) (UI and Map Visuals)
* **Backend:** [Python](https://www.python.org/)
* **AI/ML:** Custom Reinforcement Learning model (DQN - Deep Q-Network)
* **Data:** [OSMnx](https://github.com/gboeing/osmnx) (Converting city roads into graph structures)
* **Real-Time:** WebSockets (Streaming live movement to the browser)

### Architecture
1.  **Map Generation:** We use Map APIs to turn real-world city roads into graph data structures.
2.  **AI Processing:** A Python backend runs the reinforcement learning model to plan routes.
3.  **Live Stream:** WebSockets stream the snowplow decisions and movements to the frontend.
4.  **Visualization:** React renders the agents and the clearing progress on the map.

## 🚧 Challenges & Learnings

### Challenges We Ran Into
* **Messy Maps:** Real-world map data is significantly messier than it looks.
* **AI Logic:** Teaching AI not to plow the same road twice was harder than expected.
* **Performance:** Making city-sized simulations run fast enough without lag.
* **Data Sync:** Syncing real-time data between the Python backend and React frontend without crashing.
* **Debugging:** Troubleshooting AI that *looked* smart but was actually making poor
