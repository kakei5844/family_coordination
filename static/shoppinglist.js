todoMain();

function todoMain(){
    let inputElem_item,
    addButton,
    tableBodyElem;

    getElements();
    displayData();
    addListeners();

    function getElements(){
        inputElem_item = document.getElementById("item");
        addButtonElem = document.getElementById("add");
        tableBodyElem = document.getElementById("shopping_list");
    }

    function displayData(){
        fetch('/process')
            .then(res => {
                return res.json();
            })
            .then(data => {
                data.forEach(item => {
                    let trElem = document.createElement("tr");
                    tableBodyElem.appendChild(trElem);

                    // id cell
                    let tdElem = document.createElement("td");
                    tdElem.innerText = item.id;
                    trElem.appendChild(tdElem);

                    // checkbox cell
                    let checkboxElem = document.createElement("input");
                    checkboxElem.type = "checkbox";
                    checkboxElem.checked = item.checked;

                    checkboxElem.addEventListener("click", bought, false);

                    let tdElem2 = document.createElement("td");
                    tdElem2.appendChild(checkboxElem);
                    trElem.appendChild(tdElem2);

                    // item cell
                    let tdElem3 = document.createElement("td");
                    tdElem3.innerText = item.item;
                    trElem.appendChild(tdElem3);

                    // Creator cell
                    let tdElem4 = document.createElement("td");
                    tdElem4.innerText = item.creator;
                    trElem.appendChild(tdElem4);

                    // Bought by
                    let tdElem5 = document.createElement("td");
                    if (!item.checked){
                        tdElem5.innerText = '/';
                    }
                    else{
                        tdElem5.innerText = item.buyer;
                    }
                    trElem.appendChild(tdElem5);

                    // Amount
                    let tdElem6 = document.createElement("td");
                    if (!item.checked){
                        tdElem6.innerText = '/';
                    }
                    else{
                        tdElem6.innerText = item.expense;
                    }
                    trElem.appendChild(tdElem6);

                    // delete icon cell
                    let spanElem = document.createElement("span");
                    spanElem.innerText = "delete";
                    spanElem.className = "material-symbols-outlined";

                    spanElem.addEventListener("click", deleteItem, false);

                    tdElem7 = document.createElement("td");
                    tdElem7.appendChild(spanElem);
                    trElem.appendChild(tdElem7);

                    // bought function
                    async function bought(){
                        const { value: expense } = await Swal.fire({
                            title: 'Thank you for buying it!',
                            input: 'text',
                            inputLabel: 'How much is it?',
                            inputPlaceholder: 'Enter the amount you paid'
                            })

                            if (expense) {
                            Swal.fire(`Entered expense: $ ${expense}`)
                            fetch('/checked_item', {
                                method: 'POST',
                                headers: {
                                    "Content-Type": "application/json",
                                  },
                                body: JSON.stringify({
                                    'id': tdElem.innerText,
                                    'expense': expense
                                }), // body data type must match "Content-Type" header
                                }
                            ).then(() => {
                                window.location.reload();
                            })
                        }
                    }

                    // delete item function
                    function deleteItem(){
                        Swal.fire({
                            title: 'Are you sure you want to delete it?',
                            showCancelButton: true,
                            confirmButtonText: 'Yes, delete it!',
                          }).then((result) => {
                            if (result.isConfirmed) {
                                Swal.fire('Deleted!', '', 'success');
                                fetch('/delete_item', {
                                    method: 'POST',
                                    headers: {
                                        "Content-Type": "application/json",
                                      },
                                    body: JSON.stringify({
                                        'id': trElem.children[0].innerText
                                    }), // body data type must match "Content-Type" header
                                    }
                                ).then(() => {
                                    window.location.reload();
                                })
                            }
                          })
                    }
                })
            });
    }

    function addListeners(){
        addButtonElem.addEventListener("click", addEntry, false);
    }

    function addEntry(event){
        let inputValue_item = inputElem_item.value;
        let addData = {'item': inputValue_item};

        inputElem_item.value = "";

        fetch('/process', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
              },
            body: JSON.stringify(addData), // body data type must match "Content-Type" header
            }
        ).then(() => {
            window.location.reload();
        })
    }
}