const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Configure your mail transporter
const transporter = nodemailer.createTransport({
    service: 'Gmail', // You can also use services like Outlook, Yahoo, etc.
    auth: {
        user: 'your_email@gmail.com',
        pass: 'your_email_password'
    }
});

app.post('/send-confirmation', (req, res) => {
    const { email, username } = req.body;

    const mailOptions = {
        from: 'your_email@gmail.com',
        to: email,
        subject: 'Account Confirmation',
        text: `Hello ${username},\n\nYour account has been successfully created! Welcome aboard!\n\nBest Regards,\nThe Team`
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.error(error);
            return res.status(500).send('Error sending email.');
        }
        console.log('Email sent: ' + info.response);
        res.status(200).send('Confirmation email sent.');
    });
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
