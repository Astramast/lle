import numpy as np

from lle import World, Action, ObservationType
from lle import LaserSource, Gem, Laser


def test_observation_gem_collected():
    world = World.from_file("python/tests/maps/3x4_gem.txt")
    observer = ObservationType.RELATIVE_POSITIONS.get_observation_generator(world)
    world.reset()
    world.step([Action.SOUTH])
    obs0 = observer.observe()
    assert all(obs0[:, -1] == 1.0)

    world.step([Action.SOUTH])
    obs1 = observer.observe()
    assert all(obs1[:, -1] == 0.0)

    world.step([Action.NORTH])
    obs1 = observer.observe()
    assert all(obs1[:, -1] == 0.0)


def test_observe_rgb_not_empty():
    world = World.from_file("python/tests/maps/3x4_two_agents_gem.txt")
    observer = ObservationType.RGB_IMAGE.get_observation_generator(world)
    world.reset()
    image = observer.observe()
    assert image.max() > image.min()


def test_observe_layered_deactivated_laser():
    world = World.from_file("python/tests/maps/5x5_laser_2agents")
    observer = ObservationType.LAYERED.get_observation_generator(world)
    world.reset()
    layers = observer.observe()
    LASERS_0_LAYER = world.n_agents + 1
    LASERS_1_LAYER = LASERS_0_LAYER + 1
    # Laser source and laser beam in layer 0
    assert np.all(layers[:, LASERS_0_LAYER, 0, 2] == -1)
    assert np.all(layers[:, LASERS_0_LAYER, 1:4, 2] == 1)
    # Nothing in layer 1
    assert np.all(layers[:, LASERS_1_LAYER] == 0)

    # Now deactivate laser by blocking it
    world.step([Action.WEST, Action.STAY])
    layers = observer.observe()
    # Laser source and laser beam in layer 0
    assert np.all(layers[:, LASERS_0_LAYER, 0, 2] == -1)
    assert np.all(layers[:, LASERS_0_LAYER, 2:4, 2] == 0)
    # Nothing in layer 1
    assert np.all(layers[:, LASERS_1_LAYER] == 0)


def test_observe_layered_gems_walls():
    world = World.from_file("python/tests/maps/5x5_laser_1agent_1gem")
    observer = ObservationType.LAYERED.get_observation_generator(world)
    world.reset()
    layers = observer.observe()
    LASER_0_LAYER = world.n_agents + 1
    WALL_LAYER = world.n_agents
    GEM_LAYER = world.n_agents * 2 + 1
    EXIT_LAYER = -1

    for i, j in world.wall_pos:
        assert np.all(layers[:, WALL_LAYER, i, j] == 1)
    for (i, j), _ in world.gems:
        assert np.all(layers[:, GEM_LAYER, i, j] == 1)
    for i, j in world.exit_pos:
        assert np.all(layers[:, EXIT_LAYER, i, j] == 1)
    for (i, j), laser in world.lasers:
        if laser.is_on:
            assert np.all(layers[:, LASER_0_LAYER + laser.agent_id, i, j] == 1)
    for (i, j), source in world.laser_sources:
        assert np.all(layers[:, LASER_0_LAYER + source.agent_id, i, j] == -1)


def test_observe_flattened():
    map_file = "python/tests/maps/5x5_laser_1agent_1gem"
    world = World.from_file(map_file)
    observer = ObservationType.FLATTENED.get_observation_generator(world)
    assert observer.shape == (5 * 5 * (world.n_agents * 2 + 3),)
    world.reset()
    obs = observer.observe()
    assert obs.shape == (
        1,
        (world.n_agents * 2 + 3) * 5 * 5,
    )


def test_world_initial_observation():
    world = World.from_file("python/tests/maps/3x3.txt")
    observer = ObservationType.RELATIVE_POSITIONS.get_observation_generator(world)
    world.reset()
    obs0 = observer.observe()
    expected = np.array([[0.0, 0.0]])
    assert np.array_equal(expected, obs0)

    world = World(
        """
    S0 X  .
    .  .  S1
    .  .  X"""
    )
    observer = ObservationType.RELATIVE_POSITIONS.get_observation_generator(world)
    world.reset()
    obs0 = observer.observe()
    expected = np.tile(np.array([0.0, 0.0, 1 / 3, 2 / 3]), (2, 1))
    assert np.allclose(expected, obs0)

    world = World.from_file("python/tests/maps/3x4_two_agents.txt")
    observer = ObservationType.RELATIVE_POSITIONS.get_observation_generator(world)
    world.reset()
    obs0 = observer.observe()
    expected = np.tile(np.array([0.0, 0.0, 1 / 3, 1 / 2]), (2, 1))
    assert np.allclose(expected, obs0)

    world = World.from_file("python/tests/maps/3x4_two_agents_gem.txt")
    observer = ObservationType.RELATIVE_POSITIONS.get_observation_generator(world)
    world.reset()
    obs0 = observer.observe()
    expected = np.tile(np.array([0.0, 0.0, 1 / 3, 1 / 2, 1]), (2, 1))
    assert np.allclose(expected, obs0)
