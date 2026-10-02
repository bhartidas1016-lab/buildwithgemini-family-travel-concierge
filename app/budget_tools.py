"""Budget calculation tools for Family-Friendly Travel Concierge."""


def calculate_family_budget(
    num_adults: int,
    num_children: int,
    num_days: int,
    daily_meal_budget_per_person: float = 40.0,
    estimated_daily_activities_per_family: float = 60.0,
    currency: str = "USD",
) -> str:
    """Calculate the total estimated trip budget and cost breakdown for a family trip.

    Args:
        num_adults: Number of adults traveling.
        num_children: Number of children traveling.
        num_days: Duration of the trip in days.
        daily_meal_budget_per_person: Daily estimated meal budget per person in the specified currency (default 40.0).
        estimated_daily_activities_per_family: Estimated daily activity costs for the entire family in the specified currency (default 60.0).
        currency: Currency symbol or code (default 'USD').

    Returns:
        A detailed summary breakdown of estimated meal costs, activity costs, total budget, and daily average.
    """
    total_people = num_adults + num_children
    total_meals = total_people * daily_meal_budget_per_person * num_days
    total_activities = estimated_daily_activities_per_family * num_days
    total_estimated = total_meals + total_activities
    per_day_avg = total_estimated / max(1, num_days)

    return (
        f"Family Trip Budget Breakdown ({num_days} days for {num_adults} adult(s) and {num_children} child(ren)):\n"
        f"- Estimated Meal Costs ({total_people} people @ {currency} {daily_meal_budget_per_person:.2f}/person/day): {currency} {total_meals:.2f}\n"
        f"- Estimated Activity Costs (@ {currency} {estimated_daily_activities_per_family:.2f}/family/day): {currency} {total_activities:.2f}\n"
        f"- Total Estimated Trip Cost: {currency} {total_estimated:.2f}\n"
        f"- Daily Average Cost: {currency} {per_day_avg:.2f}/day"
    )
