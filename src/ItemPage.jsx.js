import React from 'react'
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import InputAdornment from '@material-ui/core/InputAdornment';
import moment from 'moment'

// TODO: Set up button functionality
class ItemPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      itemID: "",
      description: "",
      name: "",
      quantity: 1,
      buyPrice: "",
      categories: [],
      endTime: "",
      reportFlag: false,
      shippingPrice: "",
      startTime: "",
      id: "",
      startPrice: "",
      bid: false,
      bidPrice: "",
      validBid: false,
      bidHistory: [],
      expired: false,
      remainingTime: ""
    }
    this.getItem = this.getItem.bind(this)
    this.handleChange = this.handleChange.bind(this)
    this.toggleBid = this.toggleBid.bind(this)
    this.handleBid = this.handleBid.bind(this)
    this.handleBidChange = this.handleBidChange.bind(this)
    this.addToCart = this.addToCart.bind(this)
    this.addToWatchlist = this.addToWatchlist.bind(this)
    this.reportItem = this.reportItem.bind(this)
  }

  componentWillMount() {
    this.getItem();
  }

  getItem() {
    const itemID = this.props.match.params.id
    this.setState({itemID: itemID})
    fetch(`/api/items/${itemID}`)
      .then(results => {
        return results.json()
      }).then(data => {
        console.log("Input Data", data)
        this.setState({...data})
        if (this.state.bidHistory.length > 0) {
          this.setState({startingPrice: this.state.bidHistory[this.state.bidHistory.length-1]})
        }
        if (moment(Date.now()).isAfter(moment(this.state.endTime))) {
          this.setState({expired: true})
        } else {
          const duration = moment.duration(moment(this.state.endTime).diff(moment(Date.now())))
          this.setState({remainingTime: duration.humanize()})
        }
    })
  }

  handleChange = name => event => {
    this.setState({
      [name]: event.target.value,
    });
  }

  handleBidChange(event) {
    this.setState({bidPrice: event.target.value})
    if (parseFloat(this.state.bidPrice) > parseFloat(this.state.startPrice)) {
      this.setState({validBid: true})
    } else {
      this.setState({validBid: false})
    }
  }

  toggleBid() {
    this.setState({bid: !this.state.bid})
  }

  handleBid() {
    // TODO: Validate in backend as well
    fetch(`/api/items/${this.state.itemID}/bid`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userID: 'DUMMY',
        bidPrice: this.state.bidPrice,
        bidTime: Date.now()
      })
    }).then(results => {
      return results.json()
    }).then(data => {
        this.setState({startPrice: data.bidPrice})
    })
  }

  addToCart() {
    // DUMMY DATA
    const userID = "5beb3c55d5e788ace8a79665"
    fetch(`/api/users/${userID}/cart`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        _id: this.state.itemID
      })
    }).then(results => {
      return results.json()
    }).then(data => {
        console.log(data)
    })
  }

  addToWatchlist() {
    //DUMMY
    const userID = "5beb3c55d5e788ace8a79665"
    fetch(`/api/users/${userID}/watchlist`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        _id: this.state.itemID
      })
    }).then(results => {
      return results.json()
    }).then(data => {
        console.log(data)
    })
  }

  reportItem() {
    console.log("REPORT")
  }

  render() {
    return (
      <div>
        <h1>{this.state.name}</h1>
        <p> Quantity: {this.state.quantity}</p>
        <p> Time Left: {this.state.expired ? "Auction has ended" : this.state.remainingTime} </p>
        <p> Bid Price: ${this.state.startPrice} </p>
        <Button variant="contained" onClick={()=>this.toggleBid()} disabled={this.state.expired}> Bid </Button>
        {this.state.bid && !this.state.expired ? <div><form autoComplete="off">
        <TextField
            required
            label="Bid Amount"
            id="bid_price"
            margin="dense"
            InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                $
              </InputAdornment>
            ),
          }}
            value={this.state.bidPrice}
            variant="outlined"
            onChange={(event)=>this.handleBidChange(event)}
          />

        </form>
        <Button variant="contained" onClick={()=>this.handleBid()} disabled={!this.state.validBid}> Make Bid </Button>
        </div>: null}
        {this.state.buyPrice !== "0.00" ? <div><p>Buy Price: ${this.state.buyPrice}</p><Button variant="contained" onClick={()=>this.addToCart()}> Buy Now </Button></div> : ""}
        <p> Shipping price: ${this.state.shippingPrice} </p>
        <h4>Description</h4>
        {this.state.description}
        <h4>Categories</h4>
        {this.state.categories}
        <br />
        <Button variant="contained" onClick={()=>this.addToWatchlist()}>Add to Watchlist </Button>
        <Button variant="contained" onClick={()=>this.reportItem()}>Report Item </Button>
      </div>
    )
  }
}
export default ItemPage