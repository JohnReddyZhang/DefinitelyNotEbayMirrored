import React from 'react';
import PropTypes from 'prop-types';
import {withStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import moment from 'moment'

const styles = {
    card: {
        minWidth: 275,
        maxWidth: 500
    },
    bullet: {
        display: 'inline-block',
        margin: '0 2px',
        transform: 'scale(0.8)',
    },
    title: {
        fontSize: 11,
    },
    pos: {
        marginBottom: 12,
    },
};


class Notifications extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        return (
            <div style={{width: 500, right:0, position: "fixed"}}>
            {this.props.notifications.map((notification, i) =>
            (<Card key={i}>
                <CardContent>
                    <Typography variant="h5" component="h2">
                        {notification.message}
                        {notification.timestamp}
                    </Typography>
                </CardContent>
            </Card>))}
            </div>
        );
    }

}

export default withStyles(styles)(Notifications);