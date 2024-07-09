document.addEventListener('DOMContentLoaded', function() {
    // Function to display recommendations
    function displayRecommendations(recommendations) {
        console.log("Received recommendations for display:", recommendations);
        const recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = ''; // Clear previous recommendations

        if (recommendations.error) {
            recommendationsDiv.textContent = `Error: ${recommendations.error}`;
        } else if (recommendations.data && recommendations.data.recommendations) {
            console.log("Processing recommendations:", recommendations.data.recommendations);
            recommendations.data.recommendations.forEach(rec => {
                console.log("Processing recommendation:", rec);
                const recElement = document.createElement('div');
                recElement.classList.add('recommendation-item');

                const recLink = document.createElement('a');
                const recImg = document.createElement('img');
                const recText = document.createElement('div');

                recLink.href = rec.link; // Ensure this is the correct field for the URL
                recLink.target = "_blank";
                recLink.rel = "noopener noreferrer"; // Security measure

                recImg.src = rec.profile;
                recImg.alt = `${rec.channel} profile image`;
                recImg.classList.add('profile-img');

                recText.textContent = rec.channel;
                recText.classList.add('channel-name');

                recLink.appendChild(recImg);
                recLink.appendChild(recText);
                recElement.appendChild(recLink);
                recommendationsDiv.appendChild(recElement);
            });
        } else {
            recommendationsDiv.textContent = "No recommendations found.";
        }
    }

    // Add event listener for manual search
    document.getElementById('recommend-btn').addEventListener('click', function() {
        const channelUrl = document.getElementById('channel-input').value.trim();
        console.log("Channel URL:", channelUrl);

        if (channelUrl) {
            // First, get the channel name from the URL
            fetch('https://youtubechannelrecommender.onrender.com/get_channel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: channelUrl })
            })
            .then(response => {
                console.log("Response from get_channel:", response);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Data from get_channel:", data);
                if (data.error) {
                    console.error('Error fetching channel name:', data.error);
                    document.getElementById('recommendations').textContent = `Error fetching channel name: ${data.error}`;
                } else {
                    const channelName = data.channel;
                    console.log('Channel name:', channelName);

                    // Now get recommendations based on the channel name
                    return fetch('https://youtubechannelrecommender.onrender.com/recommend', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ channel: channelName, url: channelUrl })
                    });
                }
            })
            .then(response => {
                console.log("Response from recommend:", response);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Data from recommend:", data);
                if (data.error) {
                    console.error('Error fetching recommendations:', data.error);
                    document.getElementById('recommendations').textContent = `Error fetching recommendations: ${data.error}`;
                } else {
                    console.log('Recommendations received:', data);
                    displayRecommendations(data);
                }
            })
            .catch((error) => {
                console.error('Fetch error:', error);
                document.getElementById('recommendations').textContent = `Fetch error: ${error.message}`;
            });
        }
    });
});
