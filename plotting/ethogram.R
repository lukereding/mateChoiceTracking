###############
########## 6 October 2015 ###
###########################################

# contains R code to plot an ethogram-like representation of where a female was in a tank: right side, left, or neutral
# the goal is to have some quick and dirty visual representation of what a female is doing in a given trial

## to do:
### modify so that instead 

# to run: ethogram("/path/to/file.txt, name_of_trial)
# the /path/to/file.txt files is a newline separated list of sides of the tank where the female was located; each line is a frame
# each line can take one of three options: neutral, left, or right

# example: ethogram("/Volumes/LPRLABBKP/transitivity_trials/Madeline_Large_vs_Small.txt", name="madeline")


# arguments: a vector of things and a starting index
# it sees what is listed under the starting index and sees whether the same thing is in the next index
# it keeps doing this until it finds something that doesn't match whatever was under the starting index
# it returns the index of the last thing
# e.g.: x <- c("right","right","left"); find_clumps(x,1); ## returns 2
find_clumps <- function(x,start){
  if(is.numeric(start) == FALSE){
    stop("second argument must be numeric")
  }
  initial_state <- x[start]
  i = start
  while(initial_state == x[i] & i <= length(x)){
    i <- i + 1
  }
  return(i-1)
}

draw_rectangle <- function(start_x,end_x,y,offset,color,chunk_length){
  rect(start_x,y+offset,end_x,y-offset,col=color, lwd=0.5,border=NA)
}


draw_rectangles <- function(sides,i=1,end_i = 100,y_position,size,offset,part=1,col=c("#482878FF","grey80","#35B779FF")){
  i_initial = i
  
  while(i < end_i){
    new_i <- find_clumps(sides,i)
    #print(c(i, new_i))
    #print(c(i - i_initial,new_i - i_initial))
    # for error checking:
    #print ("Press [enter] to continue")
    #number <- scan(n=1)
    # or:
    #system("sleep 0.4")
 
       # this if else statement is nec. because of the modolo operations in the call to draw_rectangle
    if(new_i %% size >= i %% size){
      draw_rectangle(i - i_initial,new_i - i_initial,y_position,color = col[match(sides[i],levels(as.factor(sides)) %>% sort)],chunk_length=size,offset=offset)
      
      # if i = new_i, then behavior only appears for a second, so go to the next frame
      if(new_i == i){
        i <- i+1
      }
      else{
        i <- new_i
      }
    }
    
    else{
      print("end of the line")
      print(c(i %% size, end_i))
      draw_rectangle(i - i_initial,end_i - i_initial,y_position,color = col[match(sides[i],levels(as.factor(sides)) %>% sort)],chunk_length=size,offset=offset)
      i <- end_i
    }
  }
}

# ethogram("/Volumes/LPRLABBKP/transitivity_trials/Madeline_Large_vs_Small.txt", name="madeline")
ethogram <- function(path,name){
  op <- par(no.readonly = TRUE)
  par(lwd=1,cex=1,bg="white",xpd=FALSE,las=1)
  
  # check to make sure arugments are characters
  if(!is.character(path) | !is.character(name)){
    stop("arguments must be character strings")
  }
  
  sides_vector <- read.table(path,sep="\n")
  sides_vector <- as.vector(sides_vector[,1])
  bounds <- c(1,length(sides_vector)*0.2381,length(sides_vector)*0.2381,length(sides_vector)*0.4762,length(sides_vector)*0.4762,length(sides_vector)*0.5238,length(sides_vector)*0.5238,length(sides_vector)*0.7619,length(sides_vector)*0.7619,length(sides_vector)) %>% round(0)
  chunk_length <- bounds[2]
  chunks <- seq(0,length(sides_vector),chunk_length)
  labels <- c("background","stimuli","background","stimuli","background")
  
  # plot
  plot(1:chunk_length,seq(1,chunk_length,by=1),type="n",bty="n",xlab="time (sec.)",ylab="",yaxt='n',xaxt="n",main=name,asp=0.5)
  axis(1,at=seq(0,3000,by=500),labels=seq(0,3000,by=500)/10)
  
  off <- bounds[2]*0.05
  
  
  draw_rectangles(sides_vector,i=1,end_i = bounds[2], y_position=bounds[2],size=bounds[2],part=1,offset=off,col=c("grey60","grey90","grey20"))
  print("drew part 1")
  draw_rectangles(sides_vector,i=bounds[3],end_i = bounds[4], y_position=bounds[2]*0.75,size=bounds[2],part=2,offset=off,col=c("#440154FF","grey90","#35B779FF"))
  print("drew part 2")
  draw_rectangles(sides_vector,i=bounds[5],end_i = bounds[6], y_position=bounds[2]*0.5,size=bounds[2],part=3,offset=off,col=c("grey60","grey90","grey20"))
  print("drew part 3")
  draw_rectangles(sides_vector,i=bounds[7],end_i = bounds[8], y_position=bounds[2]*0.25,size=bounds[2],part=4,offset=off,col=c("#35B779FF","grey90","#440154FF"))
  print("drew part 4")
  draw_rectangles(sides_vector,i=bounds[9],end_i = bounds[10], y_position=bounds[2]*0,size=bounds[2],part=5,offset=off,col=c("grey60","grey90","grey20"))
  print("drew part 5")
  # draw legend
  legend(x = bounds[2]*0.45, y= bounds[2]*0.6, c("left","right","neutral","stim1","stim2"), fill=c("grey60","grey20","grey90","#440154FF","#35B779FF"),border=NA,ncol=2,bty="o", box.lwd=0.3) 
  
  
  # label
  for(i in 1:(length(labels))){
    mtext(labels[i],2,at=chunk_length - ((i-1)*0.25*chunk_length),las=2,adj=0.5)
    #text(x = 200,y=chunk_length - (0.25*(i-1)*chunk_length),labels = labels[i])
  }
  
  print(bounds)
  print(chunk_length)
  print(chunks)
  on.exit(par(op))
}
ethogram("/Volumes/LPRLABBKP/transitivity_trials/Madeline_Large_vs_Small.txt", name="madeline")
