chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('youtube.com/watch')) {
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
                const channelName = data.channel;
                console.log('Channel Name:', channelName);
                return fetch('http://127.0.0.1:5000/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ channel: channelName })
                });
            })
            .then(response => response.json())
            .then(data => {
                console.log('Recommendations:', data);
                chrome.storage.local.set({ recommendations: data.recommendations }, () => {
                    chrome.runtime.sendMessage({ action: "recommendations", data: data }, () => {
                        if (chrome.runtime.lastError) {
                            console.error('Error sending message:', chrome.runtime.lastError);
                        } else {
                            console.log('Message sent successfully');
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error:', error);
                chrome.runtime.sendMessage({ action: "recommendations", error: error.message });
            });
        });
    }
});

chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
    chrome.storage.local.get('youtubeTab', (data) => {
        if (data.youtubeTab && tabId === removeInfo.windowId) {
            chrome.storage.local.remove('youtubeTab', () => {
                console.log('YouTube URL removed');
            });
        }
    });
});
