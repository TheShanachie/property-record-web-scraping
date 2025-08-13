Selenium v4.33.0


Use of threading, use of _* for non-private-like members, ...


The app currently creates a global events handler object which shouldn't work if multiple apps are created.