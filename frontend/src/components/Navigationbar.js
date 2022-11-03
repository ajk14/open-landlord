import { Nav, Navbar, NavDropdown } from "react-bootstrap";
import { Link } from "react-router-dom";


const Navigationbar = () => {
	return (
	<>
		<Navbar bg="bg-white" expand="md">
	    <a className="navbar-brand d-lg-none d-md-none" href="/">
	    	<img src="/logo.png" alt="Albany Landlord Report Card" height="100" />
	  	</a>
	        <Navbar.Toggle aria-controls="basic-navbar-nav" />
	        <Navbar.Collapse id="basic-navbar-nav">
	          <Nav className="m-auto align-items-center">
	            <Nav.Link href="/">Search</Nav.Link>
	            <Nav.Link href="/about">About</Nav.Link>
	            <Navbar.Brand className="brand-center d-none d-lg-block d-md-block" href="/"><img src="/logo.png" alt="Albany Landlord Report Card" height="100" /></Navbar.Brand>
	            <Nav.Link href="/faq">FAQ</Nav.Link>
	            <Nav.Link target="_blank" href="https://linktr.ee/utalbany">Resources</Nav.Link>
	          </Nav>
	        </Navbar.Collapse>
	    </Navbar>
    </>
	);
}

export default Navigationbar;