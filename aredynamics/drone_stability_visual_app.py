import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import streamlit as st


AIR_DENSITY = 1.225  # kg/m^3 at sea level
GRAVITY = 9.81  # m/s^2


@dataclass
class StabilityResult:
    total_mass: float
    weight_force: float
    drag_force: float
    available_thrust: float
    required_thrust: float
    thrust_margin: float
    thrust_to_weight_ratio: float
    thrust_reserve_percent: float
    tilt_angle_degrees: float
    status: str
    risk: str
    recommendation: str


def calculate_drag_force(drag_coefficient, frontal_area, wind_speed):
    return 0.5 * AIR_DENSITY * drag_coefficient * frontal_area * wind_speed**2


def calculate_weight_force(total_mass):
    return total_mass * GRAVITY


def calculate_available_thrust(number_of_motors, thrust_per_motor):
    return number_of_motors * thrust_per_motor


def calculate_required_thrust(weight_force, drag_force):
    # A multirotor must tilt into the wind, so the thrust requirement is the
    # vector result of vertical weight and horizontal drag.
    return math.hypot(weight_force, drag_force)


def calculate_tilt_angle(weight_force, drag_force):
    if weight_force <= 0:
        return 0.0
    return math.degrees(math.atan2(drag_force, weight_force))


def classify_stability(thrust_reserve_percent, tilt_angle_degrees):
    if thrust_reserve_percent >= 30 and tilt_angle_degrees <= 20:
        return (
            "Safe to fly",
            "Low",
            "The drone has a healthy thrust reserve for hover and wind correction.",
        )

    if thrust_reserve_percent >= 5:
        return (
            "Caution",
            "Medium",
            "Flight may be possible, but the drone has limited reserve. Reduce payload or avoid stronger wind.",
        )

    return (
        "Unsafe",
        "High",
        "Do not fly in these conditions. Increase thrust, reduce payload, or reduce wind exposure.",
    )


def analyze_stability(
    drone_mass,
    payload_mass,
    number_of_motors,
    thrust_per_motor,
    drag_coefficient,
    frontal_area,
    wind_speed,
):
    total_mass = drone_mass + payload_mass
    weight_force = calculate_weight_force(total_mass)
    drag_force = calculate_drag_force(drag_coefficient, frontal_area, wind_speed)
    available_thrust = calculate_available_thrust(number_of_motors, thrust_per_motor)
    required_thrust = calculate_required_thrust(weight_force, drag_force)
    thrust_margin = available_thrust - required_thrust
    thrust_to_weight_ratio = available_thrust / weight_force
    thrust_reserve_percent = (thrust_margin / required_thrust) * 100
    tilt_angle_degrees = calculate_tilt_angle(weight_force, drag_force)
    status, risk, recommendation = classify_stability(
        thrust_reserve_percent, tilt_angle_degrees
    )

    return StabilityResult(
        total_mass=total_mass,
        weight_force=weight_force,
        drag_force=drag_force,
        available_thrust=available_thrust,
        required_thrust=required_thrust,
        thrust_margin=thrust_margin,
        thrust_to_weight_ratio=thrust_to_weight_ratio,
        thrust_reserve_percent=thrust_reserve_percent,
        tilt_angle_degrees=tilt_angle_degrees,
        status=status,
        risk=risk,
        recommendation=recommendation,
    )


def plot_force_comparison(result):
    labels = ["Weight", "Wind drag", "Required thrust", "Available thrust"]
    values = [
        result.weight_force,
        result.drag_force,
        result.required_thrust,
        result.available_thrust,
    ]
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("Force (N)")
    ax.set_title("Drone Force Balance")
    ax.grid(axis="y", alpha=0.25)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f} N",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    return fig


def show_status_message(result):
    message = (
        f"{result.status}. Risk level: {result.risk}. "
        f"{result.recommendation}"
    )

    if result.status == "Safe to fly":
        st.success(message)
    elif result.status == "Caution":
        st.warning(message)
    else:
        st.error(message)


st.set_page_config(
    page_title="Drone Stability Predictor",
    page_icon="DR",
    layout="wide",
)

st.title("Aerodynamic Drone Stability Predictor")
st.caption(
    "Estimate whether a drone has enough thrust reserve to hover and resist wind drag."
)

with st.sidebar:
    st.header("Drone Inputs")
    drone_mass = st.number_input(
        "Drone mass (kg)",
        min_value=0.1,
        value=1.2,
        step=0.1,
        help="Mass of the drone without payload.",
    )
    payload_mass = st.number_input(
        "Payload mass (kg)",
        min_value=0.0,
        value=0.3,
        step=0.1,
        help="Extra mass carried by the drone.",
    )
    number_of_motors = st.number_input(
        "Number of motors",
        min_value=1,
        value=4,
        step=1,
    )
    thrust_per_motor = st.number_input(
        "Thrust per motor (N)",
        min_value=0.1,
        value=8.0,
        step=0.5,
    )

    st.header("Aerodynamic Inputs")
    drag_coefficient = st.number_input(
        "Drag coefficient (Cd)",
        min_value=0.05,
        value=1.1,
        step=0.05,
    )
    frontal_area = st.number_input(
        "Frontal area (m^2)",
        min_value=0.01,
        value=0.08,
        step=0.01,
    )
    wind_speed = st.number_input(
        "Wind speed (m/s)",
        min_value=0.0,
        value=10.0,
        step=0.5,
    )

result = analyze_stability(
    drone_mass=drone_mass,
    payload_mass=payload_mass,
    number_of_motors=number_of_motors,
    thrust_per_motor=thrust_per_motor,
    drag_coefficient=drag_coefficient,
    frontal_area=frontal_area,
    wind_speed=wind_speed,
)

show_status_message(result)

metric_columns = st.columns(4)
metric_columns[0].metric("Total mass", f"{result.total_mass:.2f} kg")
metric_columns[1].metric("Required thrust", f"{result.required_thrust:.2f} N")
metric_columns[2].metric("Available thrust", f"{result.available_thrust:.2f} N")
metric_columns[3].metric("Thrust margin", f"{result.thrust_margin:.2f} N")

st.divider()

left_column, right_column = st.columns([1.2, 1])

with left_column:
    st.subheader("Force Comparison")
    st.pyplot(plot_force_comparison(result), use_container_width=True)

with right_column:
    st.subheader("Flight Interpretation")
    st.write(f"**Weight force:** {result.weight_force:.2f} N")
    st.write(f"**Wind drag force:** {result.drag_force:.2f} N")
    st.write(f"**Thrust-to-weight ratio:** {result.thrust_to_weight_ratio:.2f}")
    st.write(f"**Thrust reserve:** {result.thrust_reserve_percent:.1f}%")
    st.write(f"**Estimated tilt angle:** {result.tilt_angle_degrees:.1f} degrees")

    st.info(
        "This is an early design estimator. Real drone stability also depends on "
        "center of mass, motor placement, propeller efficiency, battery voltage, "
        "controller tuning, turbulence, and wind direction."
    )

