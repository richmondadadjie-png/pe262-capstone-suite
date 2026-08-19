import numpy as np
import pandas as pd


class Fluid:
    """Represents a fluid with basic thermodynamic properties."""

    PRESETS = {
        "Water": {"density": 998.2, "viscosity": 0.001002},  # 20°C
        "Air": {"density": 1.204, "viscosity": 0.00001825},  # 20°C, 1 atm
        "Crude Oil": {"density": 850.0, "viscosity": 0.050000},  # Medium crude
    }

    def __init__(self, name: str, density: float, viscosity: float):
        if density <= 0:
            raise ValueError("Density must be greater than zero.")
        if viscosity <= 0:
            raise ValueError("Viscosity must be greater than zero.")

        self.name = name
        self.density = float(density)
        self.viscosity = float(viscosity)

    @classmethod
    def from_preset(cls, preset_name: str):
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Preset '{preset_name}' not available.")
        data = cls.PRESETS[preset_name]
        return cls(name=preset_name, density=data["density"], viscosity=data["viscosity"])


class Pipe:
    """Represents a circular pipe geometry and surface roughness."""

    def __init__(self, diameter: float, length: float, roughness: float = 0.000045):
        if diameter <= 0:
            raise ValueError("Pipe diameter must be positive.")
        if length <= 0:
            raise ValueError("Pipe length must be positive.")
        if roughness < 0:
            raise ValueError("Roughness cannot be negative.")

        self.diameter = float(diameter)
        self.length = float(length)
        self.roughness = float(roughness)

    @property
    def area(self) -> float:
        return np.pi * (self.diameter / 2) ** 2


class PipeFlowSystem:
    """Calculates hydraulics for fluid flow through a pipe."""

    def __init__(self, fluid: Fluid, pipe: Pipe):
        self.fluid = fluid
        self.pipe = pipe

    def calculate_velocity(self, volumetric_flow_rate: float) -> float:
        if volumetric_flow_rate <= 0:
            raise ValueError("Flow rate must be greater than zero.")
        return volumetric_flow_rate / self.pipe.area

    def calculate_reynolds_number(self, velocity: float) -> float:
        return (self.fluid.density * velocity * self.pipe.diameter) / self.fluid.viscosity

    def calculate_friction_factor(self, reynolds: float) -> float:
        if reynolds < 2300:
            return 64.0 / reynolds
        else:
            relative_roughness = self.pipe.roughness / self.pipe.diameter
            term = (relative_roughness / 3.7) ** 1.11 + (6.9 / reynolds)
            f = (-1.8 * np.log10(term)) ** (-2)
            return float(f)

    def calculate_pressure_drop(self, volumetric_flow_rate: float) -> dict:
        v = self.calculate_velocity(volumetric_flow_rate)
        re = self.calculate_reynolds_number(v)
        f = self.calculate_friction_factor(re)
        
        dp = f * (self.pipe.length / self.pipe.diameter) * (self.fluid.density * (v**2) / 2.0)
        regime = "Laminar" if re < 2300 else ("Transitional" if re < 4000 else "Turbulent")

        return {
            "velocity_m_s": v,
            "reynolds_number": re,
            "friction_factor": f,
            "pressure_drop_pa": dp,
            "pressure_drop_kPa": dp / 1000.0,
            "flow_regime": regime
        }


class HeatTransferModel:
    """Provides Fourier Conduction and Newton's Law of Cooling routines."""

    @staticmethod
    def wall_conduction(k: float, area: float, thickness: float, t_inside: float, t_outside: float) -> float:
        if k <= 0 or area <= 0 or thickness <= 0:
            raise ValueError("Thermal conductivity, area, and thickness must be positive.")
        
        q = (k * area * (t_inside - t_outside)) / thickness
        return float(q)

    @staticmethod
    def calculate_cooling_time(mass: float, cp: float, h: float, area: float,
                               t0: float, t_target: float, t_inf: float) -> float:
        if mass <= 0 or cp <= 0 or h <= 0 or area <= 0:
            raise ValueError("Mass, specific heat capacity, heat transfer coefficient, and surface area must be positive.")
        if (t0 <= t_inf and t_target >= t0) or (t0 >= t_inf and t_target <= t_inf):
            raise ValueError("Target temperature must lie strictly between initial temperature and ambient temperature.")

        time_sec = - (mass * cp / (h * area)) * np.log((t_target - t_inf) / (t0 - t_inf))
        return float(time_sec)

    @staticmethod
    def generate_cooling_curve(mass: float, cp: float, h: float, area: float,
                               t0: float, t_inf: float, duration_sec: float, steps: int = 100) -> pd.DataFrame:
        time_array = np.linspace(0, duration_sec, steps)
        k_cool = (h * area) / (mass * cp)
        temp_array = t_inf + (t0 - t_inf) * np.exp(-k_cool * time_array)
        
        return pd.DataFrame({"Time (s)": time_array, "Time (min)": time_array / 60.0, "Temperature (°C)": temp_array})