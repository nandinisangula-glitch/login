// ================================
// 🔥 Sidebar Toggle
// ================================
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");
}

// ================================
// 🕒 Live Clock
// ================================
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const clock = document.getElementById("liveClock");

    if (clock) {
        clock.innerText = timeString;
    }
}

setInterval(updateClock, 1000);


// ================================
// 📊 Engagement Chart (Chart.js)
// ================================
function loadEngagementChart() {
    const ctx = document.getElementById('engagementChart');

    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['9AM', '10AM', '11AM', '12PM', '1PM'],
            datasets: [{
                label: 'Average Attention %',
                data: [65, 78, 85, 72, 60],
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}


// ================================
// 🔔 Alert Popup System
// ================================
function showAlert(message, type = "success") {
    const alertBox = document.createElement("div");
    alertBox.className = `alert-box ${type}`;
    alertBox.innerText = message;

    document.body.appendChild(alertBox);

    setTimeout(() => {
        alertBox.remove();
    }, 3000);
}


// ================================
// 📥 Auto Refresh Attendance Table
// ================================
function autoRefresh() {
    setTimeout(() => {
        location.reload();
    }, 30000); // refresh every 30 seconds
}


// ================================
// 📝 Admin Form Validation
// ================================
function validateStudentForm() {
    const name = document.getElementById("studentName").value;

    if (name.trim() === "") {
        showAlert("Student name cannot be empty!", "error");
        return false;
    }

    showAlert("Student Registered Successfully!", "success");
    return true;
}


// ================================
// 🎨 Smooth Page Fade-In
// ================================
document.addEventListener("DOMContentLoaded", () => {
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.transition = "opacity 1s";
        document.body.style.opacity = 1;
    }, 200);

    loadEngagementChart();
});