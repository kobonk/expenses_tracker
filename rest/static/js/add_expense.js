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

        function processCategories(callback) {
            makeRequest(
                { method: "GET", url: "/categories"},
                response => callback(JSON.parse(response))
            )
        }

        function createExpense(callback) {
            let expense = Object.keys(fieldsMap).reduce((result, currentKey) => {
                if (currentKey === "category_id") return;

                return Object.assign({}, result, { [currentKey]: fieldsMap[currentKey].value });
            }, {});

            processCategories(categories => {
                let category = categories.filter(category => category.id === fieldsMap.category_id.value)[0];

                callback(Object.assign({}, expense, { category: category }))
            });
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
            
            createExpense(expense => {
                makeRequest(
                    { method: "POST", url: "/expense", payload: JSON.stringify(expense) },
                    () => {
                        setDefaultValues();
                        enableForm();
                        expensesStatisticsList.updateRows();
                        expensesList.updateRows();
                    }
                );
                disableForm();
            });            
        };

        return {
            initialize: () => {
                form.addEventListener("submit", addExpense);
                setDefaultValues();
                enableForm();
            }
        }
    })();

    const makeRequest = function(params, callback) {
        let xhttp = new XMLHttpRequest();
    
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                callback(xhttp.response);
            }
        };

        xhttp.open(params.method, params.url, true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(params.payload);
    };

    const expensesList = (function(){
        let createHtmlRow = (date, name, category, cost) => {
            return `<tr><td>${date}</td><td>${name}</td><td>${category}</td><td>${cost.toFixed(2)}</td></tr>`;
        };

        let renderRows = (rows) => {
            document.body.querySelector("#expenses tbody").innerHTML = rows.join("");
        };

        return {
            updateRows: () => {
                makeRequest(
                    { method: "GET", url: "/expenses/30"},
                    response => {
                        let rows = JSON.parse(response).results;
                        renderRows(rows.map(row => {
                            return createHtmlRow(row.date, row.name, row.category.name, row.cost);
                        }))
                    }
                )
            }
        }
    })();

    const expensesStatisticsList = (function() {
        let createHtmlRow = (categoryName, total) => {
            return `<tr><td>${categoryName}</td><td>${total.toFixed(2)}</td><td></td></tr>`;
        };

        let renderRows = (rows) => {
            document.body.querySelector("#statistics tbody").innerHTML = rows.join("");
        };

        let updateTotal = (total) => {
            document.body.querySelector("#statistics_total").innerHTML = total.toFixed(2);
        }

        return {
            updateRows: (days=30) => {
                let date = new Date();
                let firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
                let lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
                let endTimestamp = parseInt(lastDay / 1000);
                let startTimestamp = parseInt(firstDay / 1000);

                makeRequest(
                    { method: "GET", url: `/statistics/${startTimestamp}/${endTimestamp}` },
                    response => {
                        let rows = JSON.parse(response);
                        
                        renderRows(rows.map(row => {
                            return createHtmlRow(row.category.name, row.total);
                        }));

                        updateTotal(rows.reduce((total, row) => {
                            return total + row.total;
                        }, 0))
                    }
                )
            }
        }
    })();

    const onDomContentLoaded = () => {
        addExpenseForm.initialize();
        expensesList.updateRows();
        expensesStatisticsList.updateRows();
    };

    document.addEventListener('DOMContentLoaded', onDomContentLoaded, false);

})()
