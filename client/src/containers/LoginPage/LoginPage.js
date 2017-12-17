import React from 'react';
import LoginForm from 'b:LoginForm';
import { decl } from 'bem-react-core';

export default decl({
    block : 'LoginPage',
    content() {
        return [
            <h1 key="h">Welcome!</h1>,
            <LoginForm key="f"/>
        ];
    }
});
