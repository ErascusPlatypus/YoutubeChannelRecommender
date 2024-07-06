chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('youtube.com/watch')) {
        console.log('YouTube URL detected:', tab.url);

        chrome.storage.local.set({ youtubeTab: tab.url }, () => {
            console.log('YouTube URL stored:', tab.url);

            fetch('http://127.0.0.1:5000/get_channel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: tab.url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.channel) {
                    const channelName = data.channel;
                    console.log('Channel Name:', channelName);

                    return fetch('http://127.0.0.1:5000/recommend', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ channel: channelName, url: tab.url })
                    });
                } else {
                    throw new Error('Channel name not found in API response');
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('Recommendations:', data);

                chrome.storage.local.set({ recommendations: data.recommendations }, () => {
                    chrome.runtime.sendMessage({ action: "recommendations", data: data }, (response) => {
                        if (chrome.runtime.lastError) {
                            console.error('Error sending message:', chrome.runtime.lastError);
                        } else {
                            console.log('Message sent successfully');
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching recommendations:', error);
                chrome.runtime.sendMessage({ action: "recommendations", error: error.message });
            });
        });
    }
});
