def wswd2uv(_ws,_wd):
	return -n.sin(_wd/180.*n.pi)*_ws, -n.cos(_wd/180.*n.pi)*_ws

## parameter
fs = 13.
# setting = meta['quiver']

# breakpoint()
time, height = 
dt_ws, dt_wd = dt_dic['ws'][::1], dt_dic['wd'][::1]

u, v = wswd2uv(1.,dt_wd)


# x_tick = dt_ws.asfreq(freq).index
# x_tick_lab = x_tick.strftime('%Y-%m-%d%n%X')




## plot quiver with cmap, same length quiverssss
fig, ax = subplots(figsize=(12,6),dpi=150.)

qv = ax.quiver(time,height,u.T,v.T,dt_ws.T,cmap='jet',scale=50.)

box = ax.get_position()
ax.set_position([box.x0,box.y0+0.02,box.width,box.height])
cax = fig.add_axes([.92,box.y0+0.02,.015,box.height])

cb = fig.colorbar(qv,cax=cax)

ax.tick_params(which='major',length=6.,labelsize=fs-2.)
ax.tick_params(which='minor',length=3.5)
cb.ax.tick_params(which='major',length=5.,labelsize=fs-2.)
cb.ax.tick_params(which='minor',length=2.5)

ax.set(xticks=x_tick)
ax.set_xticklabels(x_tick_lab)

ax.set_xlabel('Time',fontsize=fs)
ax.set_ylabel('Height (m)',fontsize=fs)
cb.ax.set_title('',fontsize=fs-2.)

fig.suptitle('',fontsize=fs+2.)

show()
close()