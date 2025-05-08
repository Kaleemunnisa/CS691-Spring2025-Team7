
window.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  const localAudio = document.getElementById('localAudio');
  const remoteAudio = document.getElementById('remoteAudio');

  let peerConnection;
  const config = {
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  };

  // Handle call
  socket.on('offer', async (offer) => {
    peerConnection = new RTCPeerConnection(config);
    peerConnection.ontrack = (event) => {
      remoteAudio.srcObject = event.streams[0];
    };

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));
    localAudio.srcObject = stream;

    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', answer);
  });

  socket.on('answer', async (answer) => {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
  });

  socket.on('candidate', async (candidate) => {
    if (peerConnection) {
      await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }
  });

  window.startCall = async () => {
    try {
      peerConnection = new RTCPeerConnection(config);
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          socket.emit('candidate', event.candidate);
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));
      localAudio.srcObject = stream;

      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      socket.emit('offer', offer);
    } catch (err) {
      alert("Error accessing microphone: " + err.message);
    }
  };
});
