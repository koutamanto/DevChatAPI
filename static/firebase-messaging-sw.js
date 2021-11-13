importScripts('https://www.gstatic.com/firebasejs/3.7.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.7.0/firebase-messaging.js');

firebase.initializeApp({
    'messagingSenderId': '374091982593'
});

const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
      body: payload.notification.body,
      icon: payload.notification.icon
    };
  return self.registration.showNotification(notificationTitle,notificationOptions);
});