def get_status_color(health_pct):
    if health_pct >= 80:
        return "Healthy", "#16A34A"  # Green
    elif health_pct >= 60:
        return "Slight Wear", "#2563EB" # Blue
    elif health_pct >= 40:
        return "Moderate Wear", "#F59E0B" # Orange
    else:
        return "Critical", "#DC2626" # Red

def get_status_markdown(health_pct):
    status, color = get_status_color(health_pct)
    return f"<h3 style='color: {color}; margin-top: 0px;'>{status}</h3>"
