
import streamlit as st
import math
import matplotlib.pyplot as plt

AIR_DENSITY = 1.225  # kg/m^3

def drag_force(cd, area, wind_speed):
    return 0.5 * cd * AIR_DENSITY * area * (wind_speed ** 2)

def gravity_force(mass):
    return mass * 9.81

def total_thrust(num_motors, thrust_per_motor):
    return num_motors * thrust_per_motor

def stability_check(mass, num_motors, thrust_per_motor, cd, area, wind_speed, payload):
    total_mass = mass + payload
    fg = gravity_force(total_mass)
    fd = drag_force(cd, area, wind_speed)
    ft = total_thrust(num_motors, thrust_per_motor)
    margin = ft - (fg + fd)

    if margin > 20:
        status = "Safe to Fly"
        risk = "Low"
        recommendation = "Stable hover and safe flight expected."
    elif margin > 0:
        status = "Caution"
        risk = "Medium"
        recommendation = "Reduce payload or avoid stronger winds."
    else:
        status = "Unsafe"
        risk = "High"
        recommendation = "Do not fly. Increase thrust or reduce wind exposure."

    return fg, fd, ft, margin, status, risk, recommendation

def plot_forces(fg, fd, ft):
    labels = ["Gravity", "Drag", "Thrust"]
    values = [fg, fd, ft]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylabel("Force (N)")
    ax.set_title("Drone Force Comparison")
    return fig

st.title("🚁 Aerodynamic Drone Stability Predictor")
st.write("Visual flight behavior model for drone aerodynamic stability.")

mass = st.number_input("Drone Mass (kg)", min_value=0.1, value=1.2)
payload = st.number_input("Payload Weight (kg)", min_value=0.0, value=0.3)
num_motors = st.number_input("Number of Motors", min_value=1, value=4)
thrust_per_motor = st.number_input("Thrust per Motor (N)", min_value=0.1, value=8.0)
cd = st.number_input("Drag Coefficient (Cd)", min_value=0.1, value=1.1)
area = st.number_input("Frontal Area (m²)", min_value=0.01, value=0.08)
wind_speed = st.number_input("Wind Speed (m/s)", min_value=0.0, value=10.0)

if st.button("Analyze Aerodynamic Stability"):
    fg, fd, ft, margin, status, risk, recommendation = stability_check(
        mass, num_motors, thrust_per_motor, cd, area, wind_speed, payload
    )

    st.subheader("Flight Analysis Results")
    st.write(f"**Gravity Force:** {fg:.2f} N")
    st.write(f"**Drag Force:** {fd:.2f} N")
    st.write(f"**Total Thrust:** {ft:.2f} N")
    st.write(f"**Safety Margin:** {margin:.2f} N")
    st.write(f"**Flight Status:** {status}")
    st.write(f"**Risk Level:** {risk}")
    st.write(f"**Recommendation:** {recommendation}")

    st.subheader("Visual Force Comparison")
    fig = plot_forces(fg, fd, ft)
    st.pyplot(fig)

    st.subheader("Drone Behavior Interpretation")

    if status == "Safe to Fly":
        st.write("🟢 Drone can maintain stable hover and controlled flight under current conditions.")
    elif status == "Caution":
        st.write("🟡 Drone may drift under wind pressure. Flight possible but requires careful control.")
    else:
        st.write("🔴 Drone likely becomes unstable. Strong drag or insufficient thrust may cause unsafe operation.")
