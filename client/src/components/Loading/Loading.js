import React from 'react';
import {Spin} from 'antd';
import {decl} from 'bem-react-core';
import {observer, inject} from "mobx-react";

export default decl({
    block: 'Loading',

    content({
        store,
        ...other
    }) {
        return (
            <Spin spinning={store.isLoading} {...other}>
                {this.props.children}
            </Spin>
        );
    }
}, (me) => {
    return inject("store")(observer(me));
});