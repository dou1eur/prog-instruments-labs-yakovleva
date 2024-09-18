import os
import hashlib
import sqlite3
from typing import List, Tuple

from werkzeug.utils import secure_filename
import flask

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "gif"}

app = Flask(__name__)
app.secret_key = "random string"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def getLoginDetails() -> Tuple[bool, str, int]:
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        if "email" not in session:
            loggedIn = False
            firstName = ""
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute(
                "SELECT userId, firstName FROM users WHERE email = ?",
                (session["email"],),
            )
            userId, firstName = cur.fetchone()
            cur.execute(
                "SELECT count(productId) FROM kart WHERE userId = ?",
                (userId,)
            )
            noOfItems = cur.fetchone()[0]
    return (loggedIn, firstName, noOfItems)


@app.route("/")
def root() -> str:
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT productId, name, price,"
            "description, image, stock FROM products"
        )
        itemData = cur.fetchall()
        cur.execute("SELECT categoryId, name FROM categories")
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template(
        "home.html",
        itemData=itemData,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems,
        categoryData=categoryData
    )


@app.route("/add")
def admin() -> str:
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    return render_template("add.html", categories=categories)


@app.route("/addItem", methods=["GET", "POST"])
def addItem() -> flask.Response:
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        stock = int(request.form["stock"])
        categoryId = int(request.form["category"])

        image = request.files["image"]
        imagename = ""
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            imagename = filename

        with sqlite3.connect("database.db") as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO products"
                    "(name, price, description, image, stock, categoryId)"
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (name, price, description, imagename, stock, categoryId),
                )
                conn.commit()
                msg = "Added successfully"
            except Exception:
                conn.rollback()
                msg = "Error occurred"
        print(msg)
        return redirect(url_for("root"))


@app.route("/remove")
def remove() -> str:
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT productId, name, price,"
            "description, image, stock FROM products"
        )
        data = cur.fetchall()
    return render_template("remove.html", data=data)


@app.route("/removeItem")
def removeItem() -> flask.Response:
    productId = request.args.get("productId")

    with sqlite3.connect("database.db") as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM products WHERE productId = ?",
                (productId,)
            )
            conn.commit()
            msg = "Deleted successfully"
        except Exception:
            conn.rollback()
            msg = "Error occurred"
    print(msg)
    return redirect(url_for("root"))


@app.route("/displayCategory")
def displayCategory() -> str:
    loggedIn, firstName, noOfItems = getLoginDetails()
    categoryId = request.args.get("categoryId")

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price,"
            "products.image, categories.name FROM products, categories "
            "WHERE products.categoryId = categories.categoryId AND"
            "categories.categoryId = ?"
            (categoryId,),
        )
        data = cur.fetchall()

    categoryName = data[0][4] if data else "Unknown"
    data = parse(data)
    return render_template(
        "displayCategory.html",
        data=data,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems,
        categoryName=categoryName
    )


@app.route("/account/profile")
def profileHome() -> str:
    if "email" not in session:
        return redirect(url_for("root"))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template(
        "profileHome.html",
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems
    )


@app.route("/account/profile/edit")
def editProfile() -> str:
    if "email" not in session:
        return redirect(url_for("root"))
    loggedIn, firstName, noOfItems = getLoginDetails()

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId, email, firstName, lastName, address1,"
            "address2, zipcode, city, state, country, phone"
            "FROM users WHERE email = ?",
            (session["email"],)
        )
        profileData = cur.fetchone()
    return render_template(
        "editProfile.html",
        profileData=profileData,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems
    )


@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword() -> str:
    if "email" not in session:
        return redirect(url_for("loginForm"))

    if request.method == "POST":
        oldPassword = hashlib.md5(
            request.form["oldpassword"].encode()
        ).hexdigest()
        newPassword = hashlib.md5(
            request.form["newpassword"].encode()
        ).hexdigest()

        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT userId, password FROM users WHERE email = ?",
                (session["email"],)
            )
            userId, password = cur.fetchone()

            if password == oldPassword:
                try:
                    cur.execute(
                        "UPDATE users SET password = ? WHERE userId = ?",
                        (newPassword, userId)
                    )
                    conn.commit()
                    msg = "Changed successfully"
                except Exception:
                    conn.rollback()
                    msg = "Failed"
            else:
                msg = "Wrong password"
        return render_template("changePassword.html", msg=msg)
    return render_template("changePassword.html")


@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile() -> flask.Response:
    if request.method == "POST":
        email = request.form["email"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        address1 = request.form["address1"]
        address2 = request.form["address2"]
        zipcode = request.form["zipcode"]
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        phone = request.form["phone"]

        with sqlite3.connect("database.db") as con:
            try:
                cur = con.cursor()
                cur.execute(
                    "UPDATE users SET firstName = ?, lastName = ?,"
                    "address1 = ?, address2 = ?, zipcode = ?, city = ?,"
                    "state = ?, country = ?, phone = ? WHERE email = ?",
                    (
                        firstName,
                        lastName,
                        address1,
                        address2,
                        zipcode,
                        city,
                        state,
                        country,
                        phone,
                        email,
                    ),
                )
                con.commit()
                msg = "Saved Successfully"
            except Exception:
                con.rollback()
                msg = "Error occurred"
        return redirect(url_for("editProfile"))


@app.route("/loginForm")
def loginForm() -> str:
    if "email" in session:
        return redirect(url_for("root"))
    else:
        return render_template("login.html", error="")


@app.route("/login", methods=["POST", "GET"])
def login() -> str:
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if is_valid(email, password):
            session["email"] = email
            return redirect(url_for("root"))
        else:
            error = "Invalid UserId / Password"
            return render_template("login.html", error=error)


@app.route("/productDescription")
def productDescription() -> str:
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get("productId")

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT productId, name, price, description, image, stock "
            "FROM products WHERE productId = ?",
            (productId,)
        )
        productData = cur.fetchone()
    return render_template(
        "productDescription.html",
        data=productData,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems
    )


@app.route("/addToCart")
def addToCart() -> flask.Response:
    if "email" not in session:
        return redirect(url_for("loginForm"))

    productId = int(request.args.get("productId"))

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId FROM users WHERE email = ?",
            (session["email"],)
        )
        userId = cur.fetchone()[0]
        try:
            cur.execute(
                "INSERT INTO kart (userId, productId) VALUES (?, ?)",
                (userId, productId)
            )
            conn.commit()
            msg = "Added successfully"
        except Exception:
            conn.rollback()
            msg = "Error occurred"
    return redirect(url_for("root"))


@app.route("/cart")
def cart() -> str:
    if "email" not in session:
        return redirect(url_for("loginForm"))

    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session["email"]

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId FROM users WHERE email = ?",
            (email,)
        )
        userId = cur.fetchone()[0]

        cur.execute(
            "SELECT products.productId, products.name,"
            "products.price, products.image FROM products, kart WHERE"
            "products.productId = kart.productId AND kart.userId = ?",
            (userId,)
        )
        products = cur.fetchall()
    totalPrice = sum(row[2] for row in products)
    return render_template(
        "cart.html",
        products=products,
        totalPrice=totalPrice,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems
    )


@app.route("/removeFromCart")
def removeFromCart() -> flask.Response:
    if "email" not in session:
        return redirect(url_for("loginForm"))

    email: str = session["email"]
    productId: int = int(request.args.get("productId"))

    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId FROM users WHERE email = ?",
            (email,)
        )
        userId = cur.fetchone()[0]

        try:
            cur.execute(
                "DELETE FROM kart WHERE userId = ? AND productId = ?",
                (userId, productId)
            )
            conn.commit()
            msg = "removed successfully"
        except Exception:
            conn.rollback()
            msg = "error occurred"
    return redirect(url_for("root"))


@app.route("/logout")
def logout() -> flask.Response:
    session.pop("email", None)
    return redirect(url_for("root"))


def is_valid(email: str, password: str) -> bool:
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT email, password FROM users")
    data = cur.fetchall()
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    for row in data:
        if row[0] == email and row[1] == hashed_password:
            return True
    return False


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    if request.method == "POST":
        password = request.form["password"]
        email = request.form["email"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        address1 = request.form["address1"]
        address2 = request.form["address2"]
        zipcode = request.form["zipcode"]
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        phone = request.form["phone"]

        with sqlite3.connect("database.db") as con:
            try:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (password, email, firstName, lastName,"
                    "address1, address2, zipcode, city, state, country, phone)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        hashlib.md5(password.encode()).hexdigest(), email,
                        firstName, lastName, address1, address2, zipcode,
                        city, state, country, phone
                    )
                )
                con.commit()
                msg = "Registered Successfully"
            except Exception:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)


@app.route("/registerationForm")
def registrationForm() -> str:
    return render_template("register.html")


def allowed_file(filename: str) -> bool:
    return "." in filename and \
            filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def parse(data: List[int]) -> List[List[int]]:
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == "__main__":
    app.run(debug=True)
