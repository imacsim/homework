from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

coins = [
    {
        "id": 1,
        "name": "Bitcoin",
        "symbol": "BTC",
        "price": "88500",
        "status": "В избранном",
    },
    {
        "id": 2,
        "name": "Ethereum",
        "symbol": "ETH",
        "price": "2750",
        "status": "Обычная",
    },
    {
        "id": 3,
        "name": "Solana",
        "symbol": "SOL",
        "price": "185",
        "status": "Обычная",
    }
]


def find_coin(coin_id):
    for item in coins:
        if item["id"] == coin_id:
            return item
    return None


def validate_coin(name, symbol, price):
    errors = []
    if not name:
        errors.append("Укажите название")
    if not symbol:
        errors.append("Укажите обозначение")
    if not price:
        errors.append("Укажите курс")
    else:
        try:
            if float(price) <= 0:
                errors.append("Курс должен быть больше нуля")
        except ValueError:
            errors.append("Курс должен быть числом")
    return errors


@app.route("/")
def index():
    return render_template("index.html", coins=coins)


@app.route("/coins/<int:coin_id>")
def detail(coin_id):
    coin = find_coin(coin_id)
    if coin is None:
        return "Криптовалюта не найдена", 404
    return render_template("detail.html", coin=coin)


@app.route("/coins/add", methods=["GET", "POST"])
def add_coin():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        symbol = request.form.get("symbol", "").strip()
        price = request.form.get("price", "").strip()

        errors = validate_coin(name, symbol, price)
        if errors:
            return render_template(
                "add.html",
                errors=errors,
                name=name,
                symbol=symbol,
                price=price,
            )

        new_id = max([c["id"] for c in coins]) + 1 if coins else 1
        coins.append({
            "id": new_id,
            "name": name,
            "symbol": symbol,
            "price": price,
            "status": "Обычная",
        })
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/coins/<int:coin_id>/edit", methods=["GET", "POST"])
def edit_coin(coin_id):
    coin = find_coin(coin_id)
    if coin is None:
        return "Криптовалюта не найдена", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        symbol = request.form.get("symbol", "").strip()
        price = request.form.get("price", "").strip()

        errors = validate_coin(name, symbol, price)
        if errors:
            return render_template(
                "edit.html",
                coin=coin,
                errors=errors,
                name=name,
                symbol=symbol,
                price=price,
            )

        coin["name"] = name
        coin["symbol"] = symbol
        coin["price"] = price
        return redirect(url_for("detail", coin_id=coin["id"]))

    return render_template(
        "edit.html",
        coin=coin,
        name=coin["name"],
        symbol=coin["symbol"],
        price=coin["price"],
    )


@app.route("/coins/<int:coin_id>/status", methods=["POST"])
def toggle_status(coin_id):
    coin = find_coin(coin_id)
    if coin is None:
        return "Криптовалюта не найдена", 404

    if coin["status"] == "Обычная":
        coin["status"] = "В избранном"
    else:
        coin["status"] = "Обычная"

    return redirect(url_for("detail", coin_id=coin["id"]))


@app.route("/coins/<int:coin_id>/delete", methods=["POST"])
def delete_coin(coin_id):
    coin = find_coin(coin_id)
    if coin is None:
        return "Криптовалюта не найдена", 404

    coins.remove(coin)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)