(function(){

    const addExpenseForm = (function(){
        const form = document.getElementsByName("add-expense")[0];

        const fieldsMap = {
            category_id: form["category_id"],
            cost: form["cost"],
            name: form["name"],
            purchase_date: form["purchase_date"]
        };

        const submitButton = form["submit"];

        function createExpense() {
            return Object.keys(fieldsMap).reduce((result, currentKey) => {
                return Object.assign({}, result, { [currentKey]: fieldsMap[currentKey].value });
            }, {});
        }

        function disableForm() {
            Object.values(fieldsMap).forEach(field => field.disabled = true);
            submitButton.disabled = true;
        }

        function enableForm() {
            Object.values(fieldsMap).forEach(field => field.disabled = false);
            submitButton.disabled = false;
            fieldsMap.name.focus();
        }

        function setDefaultValues() {
            Object.entries(fieldsMap).forEach(([key, field]) => {
                if (key !== "purchase_date") {
                    field.value = "";
                }
            });
            fieldsMap.purchase_date.value = formatDateString(new Date());
        }

        function formatDateString(date) {
            let dateParts = [
                date.getFullYear() + "",
                date.getMonth() + 1 + "",
                date.getDate() + ""
            ]
            return dateParts.map((part) => {
                if (part.length < 2) {
                    return "0" + part;
                } else {
                    return part
                }
            }).join("-");
        }

        function addExpense(event) {
            event.preventDefault();
            event.stopPropagation();
            
            let expense = createExpense();
            let xhttp = new XMLHttpRequest();
    
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    setDefaultValues();
                    enableForm();
                }
            };
    
            xhttp.open("POST", "/expense", true);
            xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhttp.send(JSON.stringify(expense));
    
            disableForm();
        };

        return {
            initialize: () => {
                form.addEventListener("submit", addExpense);
                setDefaultValues();
                enableForm();
            }
        }
    })();

    document.addEventListener('DOMContentLoaded', addExpenseForm.initialize, false);

})()
