$(document).ready(function () {
    // Theme toggle
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.body.classList.add(currentTheme);

        if (currentTheme === 'dark-mode') {
            toggleSwitch.checked = true;
        }
    }

    toggleSwitch.addEventListener('change', function (e) {
        if (e.target.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light-mode');
        }
    });

    // Fetch BHK and Floor options for the selected city
    $('#city').on('change', function () {
        const selectedCity = $(this).val();
        if (selectedCity) {
            $.ajax({
                url: '/get_city_details',
                method: 'GET',
                data: { city: selectedCity },
                success: function (response) {
                    if (response.success) {
                        const bhkOptions = response.bhkOptions;
                        const floorOptions = response.floorOptions;

                        $('#bhk').empty().append('<option value="" disabled selected>Select BHK</option>');
                        $('#floor').empty().append('<option value="" disabled selected>Select Floor</option>');

                        bhkOptions.forEach(option => {
                            $('#bhk').append('<option value="' + option + '">' + option + '</option>');
                        });

                        floorOptions.forEach(option => {
                            $('#floor').append('<option value="' + option + '">' + option + '</option>');
                        });
                    } else {
                        alert("Error: " + response.error);
                    }
                },
                error: function () {
                    alert("Failed to fetch city details.");
                }
            });
        }
    });

    // Form submission
    $('#rentForm').on('submit', function (e) {
        e.preventDefault();

        const formData = {
            BHK: $('#bhk').val(),
            Floor: $('#floor').val(),
            'Area Type': $('#area').val(),
            City: $('#city').val()
        };

        $.ajax({
            url: '/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                if (response.success) {
                    $('#results').html(`
                        <div class="prediction-grid">
                            <div class="prediction-column">
                                <h3>House Rent Insights</h3>
                                <div class="prediction-item">
                                    <span class="prediction-item-label">Rent Starting From</span>
                                    <span class="prediction-item-value">${response.predictions['House rent Starting from']}</span>
                                </div>
                                <div class="prediction-item">
                                    <span class="prediction-item-label">Highest Rent Upto</span>
                                    <span class="prediction-item-value">${response.predictions['Highest upto Rent']}</span>
                                </div>
                                <div class="prediction-item">
                                    <span class="prediction-item-label">Monthly Rent Average</span>
                                    <span class="prediction-item-value">${response.predictions['Monthly Rent Average']}</span>
                                </div>
                            </div>
                        </div>
                    `);
                } else {
                    $('#results').html('<p class="error">Error: ' + response.error + '</p>');
                }
            },
            error: function () {
                $('#results').html('<p class="error">Failed to fetch predictions. Try again later.</p>');
            }
        });
    });
});
