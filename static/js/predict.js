$(document).ready(function () {
    $('#rentEmiForm').on('submit', function (e) {
        e.preventDefault();

        const formData = {
            City: $('#city').val(),
            BHK: $('#bhk').val(),
            Floor: $('#floor').val(),
            'Area Type': $('#area').val()
        };

        $.ajax({
            url: '/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                if (response.success) {
                    $('#rent-results').html(`
                        <h3>Rent and EMI Insights</h3>
                        <p>Rent Starting From: ${response.predictions['House rent Starting from']}</p>
                        <p>Highest EMI: ${response.predictions['Highest Bank EMI on Monthly base']}</p>
                        <p>Monthly Rent Average: ${response.predictions['Monthly Rent Average']}</p>
                    `);
                } else {
                    $('#rent-results').html('<p>Error: ' + response.error + '</p>');
                }
            },
            error: function () {
                $('#rent-results').html('<p>Failed to fetch predictions. Try again later.</p>');
            }
        });
    });
});
