import React, {Component} from "react";
import ReactDOM from "react-dom";
import registerServiceWorker from "./registerServiceWorker";
import {Router, Route, Redirect} from "react-router-dom";
import {observer, inject} from "mobx-react";
import {Store} from "./models/store";
import {Provider} from "mobx-react";
import "b:Page";
import AppLayout from "b:AppLayout";
import IndexPage from "b:IndexPage";
import LoginPage from "b:LoginPage";
import Switch from "react-router-dom/Switch";
import {RouterStore, syncHistoryWithStore} from "mobx-react-router";
import createBrowserHistory from "history/createBrowserHistory";
import {Modal} from 'antd';

export const host = window.location.protocol + "//" + window.location.hostname

const browserHistory = createBrowserHistory();
const routingStore = new RouterStore();
const fetcher = (url, params) =>  window
  .fetch(host + ':5000/api/' + url, params)
  .then(response => response.json());

const store = Store.create({
  polls: [],
}, {
  fetch: fetcher,
  routing: routingStore,
  error: ({title, content}) => {
    Modal.error({
      title: title,
      content: (
        <div>
          <p>{content.toString()}</p>
        </div>
      ),
      onOk() {},
    });
  }
});
//store.login({name: "admin", password: "secret"});
window.store = store;

const history = syncHistoryWithStore(browserHistory, routingStore);

const PrivateRoute = inject("store")(observer(({
  store,
  component: Component,
  ...rest
}) => (
  <Route
    {...rest}
    render={props => store.user
    ? (<Component {...props}/>)
    : (<Redirect
      to={{
      pathname: "/login",
      state: {
        from: props.location
      }
    }}/>)}/>
)));

class Routes extends Component {
  render() {
    return (
      <Provider store={store} routing={routingStore}>
        <Router history={history}>
          <AppLayout>
            <Switch>
              <Redirect from="/" exact to="/list"/>
              <PrivateRoute path="/list/:pollId?" component={IndexPage}/>
              <Route path="/login" component={LoginPage}/>
              <Redirect to="/list"/>
            </Switch>
          </AppLayout>
        </Router>
      </Provider>
    );
  }
}

ReactDOM.render(
  <Routes/>, document.getElementById("root"));
registerServiceWorker();
