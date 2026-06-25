🌌 N-Body Gravitational Simulator
---

**Version 3.0** | Python | 3D Newtonian Simulation

> Simulate the gravitational dance of any set of celestial bodies, export trajectory data, and generate animated 3D GIFs.

---

## About

*Visualizer and Analyzer of Celestial Systems* is an N-body gravitational simulator written in Python. It applies Newton's Law of Universal Gravitation to compute interactions between any number of bodies over time, integrating the equations of motion using the semi-implicit Euler-Cromer method.

---

## Features

- Gravitational N-body simulation in 3D space
- Euler-Cromer integrator for improved energy conservation in orbital systems
- Gravitational softening to prevent singularities at very close distances
- Full position and velocity data export to `.txt`
- Frame-by-frame 3D trajectory plots
- Automated GIF animation generation
- Interactive command-line interface

---

## Solar System Example

The repository includes a `.txt` file containing a ready-to-use set of initial conditions for the Solar System, including the Sun and all eight planets. The values are based on physical constants from the [NASA Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/):

```python
bodies = [
    Body("Sun",     1.9885e30, (255,220,30),   0,             0,             0, 0,      0,      0),
    Body("Mercury", 3.3011e23, (169,169,169),  0,             5.7909e10,     0, -47870, 0,      0),
    Body("Venus",   4.8675e24, (230,190,90),  -1.0821e11,     0,             0, 0,     -35020,  0),
    Body("Earth",   5.9722e24, (30,144,255),   0,            -1.495978707e11,0, 29780,  0,      0),
    Body("Mars",    6.4171e23, (210,80,50),    2.2794e11,     0,             0, 0,      24070,  0),
    Body("Jupiter", 1.8982e27, (210,170,120),  0,             7.7857e11,     0, -13070, 0,      0),
    Body("Saturn",  5.6834e26, (235,210,120), -1.4335e12,     0,             0, 0,     -9690,   0),
    Body("Uranus",  8.6810e25, (140,230,240),  0,            -2.8725e12,     0, 6810,   0,      0),
    Body("Neptune", 1.0241e26, (40,70,220),    4.4951e12,     0,             0, 0,      5430,   0),
]
```

### ⚠️ A note on scientific accuracy

The physical values above planetary masses, perihelion distances, and mean orbital velocities are taken directly from the NASA Planetary Fact Sheet and are scientifically accurate.

However, **the spatial configuration is intentionally artificial**, designed for simulation purposes rather than astronomical fidelity:

- Each planet is placed along a different coordinate axis (some on +X, others on −X, +Y, −Y), so that all bodies start at their perihelion distance but spread out across perpendicular directions. This arrangement **does not correspond to any real date or alignment** of the Solar System.
- The orbital velocities used are NASA's **mean orbital velocities**, not the perihelion velocities. For strict physical consistency, bodies placed at perihelion should be given their maximum (perihelion) velocity instead, for example, Mercury's perihelion velocity is ~58.98 km/s, not the ~47.87 km/s mean used here. This combination is widely accepted in educational simulations.

This setup was chosen deliberately to give each body enough visual separation from the start, making the simulation easier to inspect and the GIF animation clearer. It produces physically plausible and stable orbits, but should not be used to reconstruct actual Solar System positions at a specific date.

**For high-fidelity, date-accurate initial conditions**, use [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/), which provides real ephemeris data for any point in time.

---

## Installation

**Requirements:** Python 3.8+

```bash
git clone https://github.com/your-username/n-body-gravitational-simulator.git
cd n-body-gravitational-simulator
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):
```
numpy
matplotlib
Pillow
```

---

## Usage

```bash
python n-body-gravitational-simulator.py
```

The program walks you through setup interactively:

1. **Number of bodies** to simulate
2. For each body: name, mass (kg), initial position XYZ (m), initial velocity XYZ (m/s), and RGB color
3. **Total simulation time** (seconds)
4. **Time step** `dt` (seconds)
5. **Output filename** for the `.txt` export
6. **Whether to generate** a 3D GIF animation

### Suggested parameters for the Solar System

| Parameter | Suggested value |
|---|---|
| Total time | `3.156e7` s (≈ 1 Earth year) |
| Time step `dt` | `3600` s (1 hour) |

> ⚠️ Smaller `dt` means higher accuracy but longer computation. For the Solar System, `dt = 3600 s` offers a good balance.

---

## Output

### `.txt` data file
Exports position (X, Y, Z) and velocity (VX, VY, VZ) for every body at every time step.

```
Time(s) | Sun_X(m) Sun_Y(m) Sun_Z(m) Sun_VX(m/s) ... | Earth_X(m) ...
0.000000 | 0.000000e+00 0.000000e+00 ...
3600.000000 | ...
```

### GIF animation
Saves an animated GIF at `simulation_3d/gravitational_animation.gif` with the 3D trajectories of all bodies. For long simulations, automatic frame sampling is applied to keep the output manageable.

---

## Physics

The simulator implements **Newton's Law of Universal Gravitation** with a softening term:

$$F = G \frac{m_1 \cdot m_2}{r^2 + \varepsilon^2}$$

where $\varepsilon$ is the softening parameter, preventing infinite forces as $r \to 0$.

Time integration uses the **Euler-Cromer method** (semi-implicit Euler):

```
v(t + dt) = v(t) + a(t) · dt        # velocity updated first
x(t + dt) = x(t) + v(t + dt) · dt   # position uses the new velocity
```

This conserves energy significantly better than the explicit Euler method, although it is not symplectic for arbitrary force formulations and still accumulates numerical error over long simulations.

---

## Constants

| Constant | Value |
|---|---|
| Gravitational constant G | `6.67430 × 10⁻¹¹ m³ kg⁻¹ s⁻²` |
| Default softening ε | `1.0 m` |

---

## Known Limitations

- The Euler-Cromer integrator accumulates error over very long simulations. For high-precision work on geological timescales, a 4th-order Runge-Kutta (RK4) or symplectic integrator of higher order is recommended.
- No physical collision detection between bodies.
- GIF generation can be slow for simulations with many time steps; automatic frame sampling kicks in above 1000 frames.
- No support for non-gravitational forces (radiation pressure, atmospheric drag, etc.).
- The simulation operates in a fixed inertial reference frame with no relativistic corrections.

---

## Gallery

### Animated Simulation

<p align="center">
  <img src="https://raw.githubusercontent.com/pancakehoneyb/N-Body-Gravitational-Simulator/main/frames-and-gif/animacao_gravitacional.gif" width="400" />
</p>

### Frame Samples

<p align="center">
  <img src="https://raw.githubusercontent.com/pancakehoneyb/N-Body-Gravitational-Simulator/main/frames-and-gif/frame_000000.png" width="280"/>
  <img src="https://raw.githubusercontent.com/pancakehoneyb/N-Body-Gravitational-Simulator/main/frames-and-gif/frame_001150.png" width="280"/>
  <img src="https://raw.githubusercontent.com/pancakehoneyb/N-Body-Gravitational-Simulator/main/frames-and-gif/frame_002190.png" width="280"/>
</p>
<p align="center">
  <em>Start of simulation &nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp; Mid simulation &nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp; Late simulation</em>
</p>

> 📁 All frames are saved under `simulation_3d/` after running the simulator with the animation option enabled.

---

## License

This project is distributed for educational and research purposes.

---

## References

- Newton, I. (1687). *Philosophiæ Naturalis Principia Mathematica*.
- Williams, D. R. (2024). *NASA Planetary Fact Sheet*. NASA GSSC. https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- Hockney, R. W. & Eastwood, J. W. (1988). *Computer Simulation Using Particles*. IOP Publishing.
