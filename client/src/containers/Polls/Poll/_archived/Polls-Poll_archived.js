import React from "react";
import { Icon } from "antd";
import { declMod } from 'bem-react-core';

export default declMod({archived: true}, {
    block: 'Polls',
    elem: 'Poll',

    content({name}) {
        return [<Icon type="lock" key="i" />, <span key="n">{name}</span>];
    }
});