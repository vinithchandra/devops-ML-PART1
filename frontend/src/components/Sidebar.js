import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Toolbar,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  BuildCircle as BuildIcon,
  Memory as MemoryIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Build Predictions', icon: <BuildIcon />, path: '/predictions' },
  { text: 'System Metrics', icon: <MemoryIcon />, path: '/metrics' },
  { text: 'Analytics', icon: <AssessmentIcon />, path: '/analytics' },
];

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              onClick={() => navigate(item.path)}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.dark',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
        <Divider />
        <List>
          <ListItem
            button
            onClick={() => navigate('/settings')}
            selected={location.pathname === '/settings'}
          >
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
}

export default Sidebar;
