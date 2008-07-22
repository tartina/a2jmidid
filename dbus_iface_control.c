/* -*- Mode: C ; c-basic-offset: 2 -*- */
/*
 * ALSA SEQ < - > JACK MIDI bridge
 *
 * Copyright (c) 2008 Nedko Arnaudov <nedko@arnaudov.name>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; version 2 of the License.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 */

#include <stdbool.h>
#include <dbus/dbus.h>

#include "dbus_internal.h"
#include "a2jmidid.h"

static
void
a2j_dbus_exit(
  struct a2j_dbus_method_call * call_ptr)
{
	g_keep_walking = false;
}

static
void
a2j_dbus_start(
  struct a2j_dbus_method_call * call_ptr)
{
	if (!a2j_start())
  {
    a2j_dbus_error(call_ptr, A2J_DBUS_ERROR_GENERIC, "a2j_start() failed.");
  }
}

static
void
a2j_dbus_stop(
  struct a2j_dbus_method_call * call_ptr)
{
	if (!a2j_stop())
  {
    a2j_dbus_error(call_ptr, A2J_DBUS_ERROR_GENERIC, "a2j_stop() failed.");
  }
}

static
void
a2j_dbus_is_started(
  struct a2j_dbus_method_call * call_ptr)
{
  dbus_bool_t is_started;

	is_started = a2j_is_started();

  a2j_dbus_construct_method_return_single(
    call_ptr,
    DBUS_TYPE_BOOLEAN,
    &is_started);
}

A2J_DBUS_METHOD_ARGUMENTS_BEGIN(exit)
A2J_DBUS_METHOD_ARGUMENTS_END

A2J_DBUS_METHOD_ARGUMENTS_BEGIN(start)
A2J_DBUS_METHOD_ARGUMENTS_END

A2J_DBUS_METHOD_ARGUMENTS_BEGIN(stop)
A2J_DBUS_METHOD_ARGUMENTS_END

A2J_DBUS_METHOD_ARGUMENTS_BEGIN(is_started)
A2J_DBUS_METHOD_ARGUMENTS_END

A2J_DBUS_METHODS_BEGIN
  A2J_DBUS_METHOD_DESCRIBE(exit, a2j_dbus_exit)
  A2J_DBUS_METHOD_DESCRIBE(start, a2j_dbus_start)
  A2J_DBUS_METHOD_DESCRIBE(stop, a2j_dbus_stop)
  A2J_DBUS_METHOD_DESCRIBE(is_started, a2j_dbus_is_started)
A2J_DBUS_METHODS_END

A2J_DBUS_IFACE_BEGIN(g_a2j_iface_control, "org.gna.home.a2jmidid.control")
    A2J_DBUS_IFACE_EXPOSE_METHODS
A2J_DBUS_IFACE_END
