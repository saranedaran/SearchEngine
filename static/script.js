let currentPage = 1;
const resultsPerPage = 5;
let allResults = [];
let totalResults = 0;

document.getElementById("searchForm").addEventListener("submit", function(event) {
    event.preventDefault();
    currentPage = 1;
    
    // Determine which search is being performed based on form inputs
    const isCustomerSearch = document.getElementById("category") && document.getElementById("searchInput");
    
    if (isCustomerSearch) {
        fetchCustomerResults();
    } else {
        fetchProductResults();
    }
});

function fetchCustomerResults() {
    const category = document.getElementById("category").value;
    const searchInput = document.getElementById("searchInput").value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category, searchInput }),
    })
    .then(response => response.json())
    .then(data => {
        allResults = data.results || [];
        totalResults = allResults.length;
        displayResults('customer');
        managePaginationButtons();
    })
    .catch(error => console.error('Error:', error));
}

function fetchProductResults() {
    const column = document.getElementById("column").value;
    const value = document.getElementById("value").value;

    fetch('/search_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            column: column,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        allResults = data.results || [];
        totalResults = data.totalResults || 0;
        displayResults('product');
        managePaginationButtons();
    })
    .catch(error => console.error('Error:', error));
}

function displayResults(type) {
    const tbody = document.querySelector("#resultsTable tbody");
    tbody.innerHTML = ""; 

    const start = (currentPage - 1) * resultsPerPage;
    const end = start + resultsPerPage;
    const paginatedResults = allResults.slice(start, end);  

    if (paginatedResults.length > 0) {
        paginatedResults.forEach(item => {
            const row = document.createElement("tr");

            if (type === 'customer') {
                row.innerHTML = `
                    <td>${item.CustomerId}</td>
                    <td>${item.Customer_Name}</td>
                    <td>${item.Country}</td>
                    <td>${item.Customer_Currency}</td>
                `;
            } else if (type === 'product') {
                row.innerHTML = `
                    <td>${item.ProductId}</td>
                    <td>${item.ProductFamily}</td>
                    <td>${item.ProductLine}</td>
                    <td>${item.ProductGroup}</td>
                    <td>${item.Status}</td>
                    <td>${item.ProductSubGroup}</td>
                    <td>${item.Stock}</td>
                    <td>${item.Color}</td>
                `;
            }
            tbody.appendChild(row);
        });
    } else {
        const colSpan = type === 'customer' ? 4 : 8;
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan='${colSpan}'>No ${type === 'customer' ? 'customers' : 'products'} found.</td>`;
        tbody.appendChild(row);
    }
}

function managePaginationButtons() {
    const maxPage = Math.ceil(totalResults / resultsPerPage);
    document.getElementById("prevPage").style.display = currentPage > 1 ? "inline-block" : "none";
    document.getElementById("nextPage").style.display = currentPage < maxPage ? "inline-block" : "none";
}

function changePage(direction) {
    const maxPage = Math.ceil(totalResults / resultsPerPage);
    const newPage = currentPage + direction;

    if (newPage >= 1 && newPage <= maxPage) {
        currentPage = newPage;

        // Determine which results to display
        const isCustomerSearch = document.getElementById("category") && document.getElementById("searchInput");
        displayResults(isCustomerSearch ? 'customer' : 'product');
        
        managePaginationButtons();
    }
}
