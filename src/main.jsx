// Import dependencies
import React from 'react';
import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom';
import * as ReactDOM from 'react-dom/client';
import ConfigureTab from './configure-tab';

const App = () => {
    return (
        <>
            <nav className="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
                <div className="container">
                    <Link className="navbar-brand" to="/">Sounding Rocket Mission Simulator</Link>
                </div>
            </nav>
            <div className="container">
                <ul className="nav nav-tabs" role="tablist">
                    <li className="nav-item" role="presentation">
                        <NavLink className="nav-link" to="/">Configure</NavLink>
                    </li>
                    <li className="nav-item" role="presentation">
                        <NavLink className="nav-link" to="/run">Run</NavLink>
                    </li>
                    <li className="nav-item" role="presentation">
                        <NavLink className="nav-link" to="/manual">Manual</NavLink>
                    </li>
                    <li className="nav-item" role="presentation">
                        <NavLink className="nav-link" to="/telemetry">Telemetry</NavLink>
                    </li>
                </ul>
                <div className="tab-content py-2">
                    <Routes>
                        <Route path="/" exact Component={ConfigureTab}></Route>
                        <Route path="/run" exact Component={ConfigureTab}></Route>
                        <Route path="/manual" exact Component={ConfigureTab}></Route>
                        <Route path="/telemetry" exact Component={ConfigureTab}></Route>
                    </Routes>
                </div>
            </div>
        </>
    );
}

// Render to the DOM
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BrowserRouter><App /></BrowserRouter>);
