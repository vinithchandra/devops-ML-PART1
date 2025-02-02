import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Badge } from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ flexGrow: 1, cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          CI/CD Quality Gate
        </Typography>
        
        <IconButton color="inherit">
          <Badge badgeContent={4} color="secondary">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        
        <IconButton 
          color="inherit"
          onClick={() => navigate('/settings')}
        >
          <SettingsIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
