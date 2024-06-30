document.addEventListener('DOMContentLoaded', function() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === "recommendations") {
            console.log("Received recommendations message:", message);

            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = ''; // Clear previous recommendations

            if (message.error) {
                recommendationsDiv.textContent = message.error;
            } else if (message.data && message.data.recommendations) {
                console.log("Processing recommendations:", message.data.recommendations);
                message.data.recommendations.forEach(rec => {
                    const recElement = document.createElement('p');
                    const recLink = document.createElement('a');
                    recLink.href = `https://www.youtube.com/channel/${rec.channel}`;
                    recLink.target = "_blank";
                    recLink.textContent = rec.channel;
                    recElement.appendChild(recLink);
                    recommendationsDiv.appendChild(recElement);
                });
                // Store recommendations in local storage
                chrome.storage.local.set({ recommendations: message.data.recommendations });
            } else {
                recommendationsDiv.textContent = "No recommendations found.";
            }
        }
    });

    // Load stored recommendations when the popup is opened
    chrome.storage.local.get('recommendations', (data) => {
        if (data.recommendations) {
            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = ''; // Clear previous recommendations
            data.recommendations.forEach(rec => {
                const recElement = document.createElement('p');
                const recLink = document.createElement('a');
                recLink.href = `https://www.youtube.com/channel/${rec.channel}`;
                recLink.target = "_blank";
                recLink.textContent = rec.channel;
                recElement.appendChild(recLink);
                recommendationsDiv.appendChild(recElement);
            });
        }
    });

    // Add event listener for manual search
    document.getElementById('recommend-btn').addEventListener('click', function() {
        const channelName = document.getElementById('channel-input').value.trim();
        if (channelName) {
            fetch('http://127.0.0.1:5000/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ channel: channelName })
            })
            .then(response => response.json())
            .then(data => {
                const recommendationsDiv = document.getElementById('recommendations');
                recommendationsDiv.innerHTML = ''; // Clear previous recommendations
                if (data.error) {
                    recommendationsDiv.textContent = data.error;
                } else {
                    data.recommendations.forEach(rec => {
                        const recElement = document.createElement('p');
                        const recLink = document.createElement('a');
                        recLink.href = `https://www.youtube.com/channel/${rec.channel}`;
                        recLink.target = "_blank";
                        recLink.textContent = rec.channel;
                        recElement.appendChild(recLink);
                        recommendationsDiv.appendChild(recElement);
                    });
                    // Store recommendations in local storage
                    chrome.storage.local.set({ recommendations: data.recommendations });
                }
            })
            .catch(error => {
                console.error('Error fetching recommendations:', error);
            });
        }
    });
});
