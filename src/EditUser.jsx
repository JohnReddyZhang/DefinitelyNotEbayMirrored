import React from 'react'
import ReactDOM from 'react-dom';
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import { withRouter, Redirect } from 'react-router';
import InputAdornment from '@material-ui/core/InputAdornment';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import Input from '@material-ui/core/Input';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import InputLabel from '@material-ui/core/InputLabel';



// TODO: Sanitize inputs
// TODO: Add functionality to suspend and delete account
class EditUser extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      _id: "",
      watchlist: [],
      cart: [],
      isAdmin: false,
      isActive: true,
      profile: {}
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.getUser = this.getUser.bind(this);
    this.suspendAccount = this.suspendAccount.bind(this);
    this.deleteAccount = this.deleteAccount.bind(this);
  }

  componentWillMount() {
    // Handle user details
    const { userProfile, getProfile } = this.props.auth
    if (!userProfile) {
      getProfile((err, profile) => {
        this.setState({profile})
        this.getUser(profile.sub)
      })
    } else {
      this.setState({ profile: userProfile })
      this.getUser(userProfile.sub)
    }
  }

  getUser(userID) {
    fetch(`/api/users/${userID}`)
      .then(results => {
        return results.json()
      }).then(data => {
        console.log(data)
        this.setState({...data})
    })
  }

  handleChange = name => event => {
    this.setState({
      [name]: event.target.value,
    });
  };

  handleSubmit() {
    const userID = this.state._id;
    if (!userID.startsWith('auth0')) {
        alert("You can't modify your email related to Google!")
    } else {
        fetch(`/api/users/${userID}`, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: this.state.email
            })
        }).then(results => {
            return results.json()
        }).then(data => {
            if (data._id) {
                this.props.auth.editUser(this.state)
                this.setState({redirect: true})
            }
        });
    }
  }

  suspendAccount() {
    const userID = this.state._id;
    fetch(`/api/users/${userID}`, {
        method: 'PUT',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            isActive: !this.state.isActive
        })
    }).then(results =>{
      return results.json()
    }).then( data => {
      // console.log(data)
        if (data._id) {
          this.setState({redirect: true})
        }
    })
  }

  deleteAccount() {
    const userID = this.state._id;
    // Pop a confirmation
    if (confirm("We are sorry to see you go...\nAre you sure you want to delete your account?")) {
        console.log("deleting " + userID);
        // TODO: does this redirects already?
        this.props.auth.deleteUser(userID);
        this.props.auth.logout();
        // Call delete route
        fetch(`/api/users/${userID}`,
            {method: "DELETE"})
            .then(result => {
                return result
            })
    } else {
        alert("Deleten't yourself.");
        console.log("Deleten't yourself.");
    }

  }

  render() {
    if (this.state.redirect) {
      return <Redirect push to="/" />;
    }
    return(
      <div style={{ margin: '10px'}}>
        <h1>Edit Account</h1>
        <h2> Change Email </h2>
        <form noValidate autoComplete="off">
          <TextField
            required
            label="Email"
            id="email"
            defaultValue={this.state.email}
            value={this.state.email}
            onChange={this.handleChange('email')}
          />
          <br />
      </form>
      <Button onClick={()=>this.handleSubmit()}> Submit </Button>
      {this.state.isActive ? <h2>Suspend Account</h2> : <h2>Activate Account</h2> }
      <Button onClick={()=>this.suspendAccount()}>  {this.state.isActive ? 'Suspend' : 'Activate'}  </Button>
      <h2> Delete Account </h2>
      <Button onClick={()=>this.deleteAccount()}> Delete </Button>
      </div>
    )
  }
}
export default withRouter(EditUser)