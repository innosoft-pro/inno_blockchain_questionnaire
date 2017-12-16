import './IndexPage.css';
import React, {Component} from 'react';
import IndexHello from '../../components/IndexHello/IndexHello';

export default class IndexPage extends Component {
    render() {
        return (
            <div className="IndexPage">
                <IndexHello />
            </div>
        );
    }
} 
