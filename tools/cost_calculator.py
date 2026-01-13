def calculate_monthly_cost(calls_per_month: int) -> dict[str, float]:
    # Compute (Cloud Run)
    compute = calls_per_month * 0.0001  # 0.1 baht per call

    # Database (Cloud SQL)
    db_storage_gb = calls_per_month * 0.001  # 1 MB per call
    db_cost = db_storage_gb * 10  # 10 baht per GB

    # Network egress
    egress_gb = calls_per_month * 0.0005  # 0.5 MB per call
    egress_cost = egress_gb * 5  # 5 baht per GB

    total = compute + db_cost + egress_cost
    return {
        "calls": calls_per_month,
        "compute": compute,
        "database": db_cost,
        "network": egress_cost,
        "total": total,
        "cost_per_call": total / calls_per_month,
    }
