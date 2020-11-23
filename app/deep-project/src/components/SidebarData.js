import React from 'react';
import * as FaIcons from 'react-icons/fa';
import * as AiIcons from 'react-icons/ai';
import * as IoIcons from 'react-icons/io';

export const SidebarData = [
  {
    title: 'Home',
    path: '/',
    icon: <AiIcons.AiFillHome />,
    cName: 'nav-text'
  },
  {
    title: 'Run detection',
    path: '/detection',
    icon: <IoIcons.IoIosFingerPrint />,
    cName: 'nav-text'
  },
  {
    title: 'Team',
    path: '/team',
    icon: <IoIcons.IoMdPeople />,
    cName: 'nav-text'
  },
  {
    title: 'Fork on github',
    path: '/github',
    icon: <IoIcons.IoIosGitNetwork />,
    cName: 'nav-text'
  },
  {
    title: 'Report an issue',
    path: '/issue',
    icon: <IoIcons.IoIosBug />,
    cName: 'nav-text'
  },
  {
    title: 'Contact us',
    path: '/message',
    icon: <IoIcons.IoIosMail />,
    cName: 'nav-text'
  },
  {
    title: 'Logout',
    path: '/logout',
    icon: <IoIcons.IoIosLogOut />,
    cName: 'nav-text'
  }
];