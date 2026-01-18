# Simulation Configuration Constants
# Adjust these values to control simulation behavior

# Socket update interval in seconds
# Lower values = more frequent updates (but more network traffic)
# Higher values = less frequent updates (but less network traffic)
SIMULATION_UPDATE_INTERVAL = 0.05  # Update every 50ms

# Simulation step delay in seconds
# Time to wait between simulation steps (world.play() calls)
SIMULATION_STEP_DELAY = 0.01  # 10ms between steps

# Training Configuration
MODEL_SAVE_INTERVAL = 100  # Save model every N training steps
TRAINING_BATCH_SIZE = 64
TRAINING_BUFFER_SIZE = 100_000
