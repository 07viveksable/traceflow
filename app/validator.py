def validate_data(data):
    if not data:
        raise ValueError("Input data is empty")

    required_columns = [
        "id",
        "name",
        "city",
        "product",
        "amount",
        "status"
    ]

    for row in data:

        for column in required_columns:
            if column not in row:
                raise ValueError(
                    f"Missing required column: {column}"
                )

        if not row["name"]:
            raise ValueError(
                f"Name is empty for ID {row['id']}"
            )

        try:
            amount = float(row["amount"])
        except ValueError:
            raise ValueError(
                f"Invalid amount for ID {row['id']}"
            )

        if amount < 0:
            raise ValueError(
                f"Negative amount for ID {row['id']}"
            )

    return True