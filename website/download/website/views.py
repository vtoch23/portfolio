from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import random
import difflib
from .models import LotteryNumbers, generate_strong_password, filter_forbidden, Investment, is_it_valid, wordlist
views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("index.html")

con = sqlite3.connect("names.db", check_same_thread=False)
db = con.cursor()
db.execute("BEGIN TRANSACTION")

print("connected")

SPORTS = [
    "Basketball",
    "Football",
    "Volleyball"
]

registrants = {}

@views.route("/spellcheck")
def spellcheck():
    print("spellcheck opened")
    return render_template("spellcheck.html")

@views.route("/spellcheck-done", methods=["POST", "GET"])
def spellcheck_done():
    words = wordlist()
    sentence = request.form.get("sentence")
    errors = [] 
    for word in sentence.split(' '):
        if not word.lower() in words:
            print("*" + word + "* ", end="")
            errors.append(word)
    suggestions = {}
    for word in errors:
        close_matches = difflib.get_close_matches(word, 
                wordlist())
        suggestions[word] = close_matches
    if suggestions and errors:    
        return render_template("spellcheck.html", errors = errors, suggestions = suggestions)
    else:
        return render_template("spellcheck.html")    
@views.route('/invest/<location>')
def profile(location):
   print("redirecting")
   return redirect(url_for('views.investment', anchor={location}))

@views.route("/investment", methods=["POST", "GET"])
def investment():
    print("investment opened")
    return render_template("investment.html")

@views.route("/investment-calc", methods=["POST", "GET"])
def investment_calc():
    print("investment calculation opened")
    
    try: 
        purchase_price = request.form.get("price")
        purchase_price = int(purchase_price)
    except:
        return render_template("failure-invest.html", message = "Please enter a purchase price in numbers only.")    
    print(f"Received purchase price is: {purchase_price}")
    
    try:    
        deposit = request.form.get("deposit")
        deposit = int(deposit)
    
    except:
        return render_template("failure-invest.html", message = "Please enter a deposit amount in numbers only.")     
    
    print(f"received deposit percent is: {deposit}")

    try:
        mortgage_term = request.form.get("term")
        mortgage_term = int(mortgage_term)
    
    except:
        return render_template("failure-invest.html", message = "Please enter a mortgage term in numbers only.")
    
    print(f"received mortgage term is: {mortgage_term}")
    
    try:    
        rate = request.form.get("rate")
        rate = float(rate)
    except:
        return render_template("failure-invest.html", message = "Please enter an interest rate in numbers only.")    
    
    print(f"the interest rate is: {float(rate)}")  
    
    try:
        fixed_period = request.form.get("fixed")
        fixed_period = int(fixed_period)
    except:
        return render_template("failure-invest.html", message = "Please enter a fixed period in numbers only.")    
    
    print(f"received fixed period is : {fixed_period}")
    
    try:
        increase = request.form.get("increase")
        increase = int(increase)
    except:
        return render_template("failure-invest.html", message = "Please enter an annual increase in numbers only.")    

      
    rate = float(round((rate/100),2))
    print("creating object")
    
    try:
        invest = Investment(int(purchase_price), float(deposit), int(mortgage_term), int(fixed_period), float(rate))
        print(invest.calc_deposit())
        print("calculating deposit")
        calculated_deposit = invest.calc_deposit()
        print(f"deposit received from object is: {calculated_deposit}")
        mortgage = invest.mortgage_calc()
        print(mortgage)
        salary = invest.salary()
        print(salary)
        payment = invest.monthly()
        print(payment)
        outstanding = int(invest.balance())
        newPrice = invest.new_price(int(purchase_price), int(increase), int(fixed_period)) 
        equity = round(newPrice - outstanding)
        new_deposit = float(round((equity/newPrice)*100, 2))
        ltv1 = int(round((mortgage/int(purchase_price))*100))
        print(f"{ltv1}%")
        ltv2 = int(round((int(outstanding)/newPrice)*100))
        print(f"{ltv2}%")
        new_salary = int(outstanding/4.75)
        dep = int(purchase_price)*0.05
        print(calculated_deposit)
        dep2 = calculated_deposit > 5
        return render_template('investment.html', fixed_period=fixed_period, increase = increase, rate=rate*100, mortgage_term=mortgage_term, deposit=deposit, dep2=dep2, mortgage=mortgage, payment=payment, purchase_price=purchase_price, calculated_deposit=calculated_deposit, salary=salary, newPrice=newPrice, equity=equity, outstanding=outstanding, new_deposit=new_deposit, ltv1=ltv1, ltv2=ltv2, new_salary=new_salary, dep=dep)
        
    except:
        return render_template("failure-invest.html", message="Invalid input, please try again.")
        

@views.route("/games", methods=["POST", "GET"])
def games():
    print("games opened")
    return render_template("games.html")

@views.route("/games-open", methods=["POST", "GET"])
def games_open():
    print("opening game")
    return render_template("games.html")

@views.route("/properties", methods=["POST", "GET"])
def properties():
    print("properties opened")
    properties = [
        {property1: {location: "London",
                      size: 100,
                      price: 300000,
                      rooms: 4}},
        {property2: {location: "Paris",
                      size: 130,
                      price: 450000,
                      rooms: 6} },
        {property3: {location: "Singapore",
                      size: 70,
                      price: 200000,
                      rooms: 3}  }                          
    ]
    return render_template("properties.html", properties=properties)

@views.route("/files", methods=["POST", "GET"])
def files():
    print("files opened")
    return render_template("files.html")

@views.route("/names-db", methods=["POST", "GET"])
def name_db():
    print("names opened")
    return render_template("name_age.html", sports=SPORTS)
  
@views.route("/register", methods=["POST", "GET"])
def register():
    print("names submitted")
    print()
    name = request.form.get("name")
    print(name)
    age = request.form.get("age")
    print(age)
    sport = request.form.get("sport")
    print(sport)

    if not name or not age or not sport in SPORTS:
        print("missing input")
        return render_template("failure.html", message = "Missing input")
    else:
        registrants[name] = []
        registrants[name].append(age)
        registrants[name].append(sport)
    print()
    print("names inserted into database")
    #people = db.execute('SELECT * FROM names')
   
    #db.execute("COMMIT")
    #return render_template("names-final.html", people=people)
    if len(registrants) > 0:
        message = "The names have been submitted into the database"
    elif len(registrants) == 0:
        message = "Plese submit an athlete"
    return render_template("name_age.html", registrants=registrants, sports=SPORTS, message=message)

@views.route("/test", methods=["POST", "GET"])
def test():
    name = request.form.get("name")
    print(name)
    age = request.form.get("age")
    print(age)
    sport = request.form.get("sport")
    print(sport)
    if not name or not age or not sport in SPORTS:
        print("missing input")
        return render_template("failure.html", message = "Missing input")
    else:
        db.execute("insert into names (name, age) VALUES(?,?)", (name, age))
        print("name, age inserted")
        
    return render_template("name_age.html", registrants=registrants, sports=SPORTS)

@views.route("/search", methods=["POST", "GET"])
def search_names():
    sport = request.form.get("sport2")
    people = {}
    for name, value in registrants.items():
        currentage = value[0]
        currentsport= value[1]
        if currentsport == sport:
            people[name] = []
            people[name].append(currentage)
            people[name].append(currentsport)
        else:
            pass    
    print(f"new list: {people}")
    if len(people) > 0:
        message1 = "Current registered athletes"
    elif len(people) == 0:
        message1 = f"No current registered athletes with {sport}"        
    return render_template("name_age.html", people=people, sports=SPORTS, message1=message1, sport=sport, registrants=registrants)
    

@views.route("/test2", methods=["POST", "GET"])
def test2():
    return render_template("test.html", sport=SPORTS, registrants=registrants)

@views.route("/words", methods = ["POST", "GET"])
def words():
    return render_template("words.html")

@views.route("/orders", methods = ["POST", "GET"])
def orders():
    return render_template("orders.html")

@views.route("/login", methods = ["POST", "GET"])
def login():
    return render_template("login.html")

@views.route("/forbidden", methods = ["POST", "GET"])
def forbidden():
    return render_template("forbidden.html")

@views.route("/forbidden-clean", methods=["GET", "POST"])
def forbidden_clean():
    sentence = request.form.get("sentence")
    filtered = filter_forbidden(sentence, "*!?:,.£$%&@<>")
    return render_template("forbidden-clean.html", filtered=filtered)

@views.route("/password", methods = ["POST", "GET"])
def password():
    return render_template("password.html")

@views.route("/pass-r", methods = ["POST", "GET"])
def pass_r():
    var = request.form.get("number")
    if generate_strong_password(var):
        print(f"received number of letters {var}")
        password = generate_strong_password(var)
    else:
        return render_template("failure-pass.html")
    print(f"received password back: {generate_strong_password(var)}")
    return render_template("password.html", password=password)

@views.route("/lottery", methods = ["POST", "GET"])
def lottery():
    return render_template("lottery.html")

@views.route("/lottery-play", methods=["POST", "GET"])
def lottery_play():
    try:
        user_numbers = ""
        user_numbers+=(request.form.get("number1"))+ " "
        user_numbers+=(request.form.get("number2"))+ " "
        user_numbers+=(request.form.get("number3"))+ " "
        user_numbers+=(request.form.get("number4"))+ " "
        user_numbers+=(request.form.get("number5"))+ " "
        user_numbers+=(request.form.get("number6"))+ " "
        user_numbers+=(request.form.get("number7"))+ " "
        print(f"the submitted numbers are: {user_numbers}")
        numbers = list(map(int, user_numbers.split()))
        assert len(numbers) == 7
        for number in numbers:
            if number > 40 or number < 1:
                return render_template("failure-lottery.html")
        print(f"numbers to be sent to lottery are: {numbers}")
        randoms = random.sample(range(0, 41), 7)
        print(f"lottery numbers today are: {randoms}")
        nums = LotteryNumbers(randoms)
        hits_number = nums.number_of_hits(numbers)
        hits = nums.hits_in_place(numbers)
        return render_template("Lottery-result.html", randoms = randoms, hits_number = hits_number, hits=hits, numbers=numbers)
    except:
        return render_template("failure-lottery.html")

@views.route("/products", methods = ["POST", "GET"])
def products():
    return render_template("products.html")

@views.route("/pic", methods = ["POST", "GET"])
def pic():
    return render_template("pic.html")

@views.route("/pic_check", methods=["POST", "GET"])
def pic_check():
    check = is_it_valid(request.form.get("code"))
    print(check)
    if check == True:
        code = request.form.get("code")
    else:
        code = request.form.get("code")    
        
    return render_template("pic.html", code=code, check=check)
   

@views.route("/about", methods = ["POST", "GET"])
def about():
    return render_template("about.html")

@views.route("/contact", methods = ["POST", "GET"])
def contact():
    return render_template("contact.html")
