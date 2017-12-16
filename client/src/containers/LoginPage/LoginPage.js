import './LoginPage.css';
import React, {Component} from 'react';
import LoginForm from '../../components/LoginForm/LoginForm';

export default class LoginPage extends Component {
    render() {
        return (
            <div className="LoginPage">
                <h1>Login</h1>
                <LoginForm />
            </div>
        );
    }
} 