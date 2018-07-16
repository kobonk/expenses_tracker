(function(){

    function initialize() {
        let form = document.getElementsByName("add-expense")[0];

        form.addEventListener("submit", addExpense);
    };
    
    function addExpense(event) {
        event.preventDefault();
        event.stopPropagation();

        let name = document.getElementsByName("name")[0].value;
        let category_id = document.getElementsByName("category_id")[0].value;
        let purchase_date = document.getElementsByName("purchase_date")[0].value;
        let cost = document.getElementsByName("cost")[0].value;
        
        let expense = { name, category_id, purchase_date, cost };

        let xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log("Expense added.");
            }
        };

        xhttp.open("POST", "/expense", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify(expense));
    };

    document.addEventListener('DOMContentLoaded', initialize, false);

})()
